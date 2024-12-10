# main.py

from app import app
from db_setup import init_db, db_session
from forms import ProteinSearchForm
from flask import flash, render_template, request, redirect
from models import Yeast
from table import Results
#from numpy import genfromtext
import pandas as pd

init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    search = ProteinSearchForm(request.form)
    #print("Search string: ",search)
    if request.method == 'POST':
        return search_results(search)

    return render_template('index.html', form=search)


@app.route('/results', methods=['POST'])
def search_results(search):

    results = []
    search_string = search.data['search']
    print(search_string)
    gene_name = search_string
    if search_string:
        if search.data['select'] == 'Yeast':
            
            qry = db_session.query(Yeast).filter(
                Yeast.uniprot_id.contains(search_string))
            results = qry.all()
            if results:
                gene_name = qry.first().gene
            #print(search_string, results)

            if not results: #First checking if user entered uniprot else checking in gene name and setting search string to uniprot id
                qry = db_session.query(Yeast).filter(
                    Yeast.gene.contains(search_string))
                results = qry.all()
                search_string = qry.first().uniprot_id

            for r in results:
                if not isinstance(r.spectral_count, int):
                    r.spectral_count = int.from_bytes(r.spectral_count,'little')
            #print(int.from_bytes(qry.first().spectral_count, byteorder='little'))
    else:
        flash('No protein entered!')
        return redirect('/')
    
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        prot_len_df = pd.read_csv('./data/4932.txt', sep='\t', header=None)
        prot_length = prot_len_df.loc[prot_len_df[0] == search_string][1]
        pfam_dom = protein_pfam_domains(search_string)
        phospho_sites = protein_phosphosites(search_string)
        insider = protein_insider_res(search_string)
        consolidated_insider = consolidate(insider)
        # Map phos sites to insider residues to determine which ones to highlight on webpage
        phospho_sites = map_phos_sites_to_insider(phospho_sites, insider)

        table = Results(results)
        table.border = True
        return render_template('results.html', name=gene_name, pfam_table=pfam_dom, phos_table=phospho_sites, insider_table=insider, cons_insider=consolidated_insider, prot_len=prot_length, table=table, form=search)

def consolidate(insider):
    df_insider = pd.read_json(insider, orient='records')
    column_names = ['P1_IRES','Source','gene_name']
    temp_insider = pd.DataFrame(columns = column_names)
    #print(list(set(df_insider["P1_IRES"].values.tolist())))
    #print(list(df_insider))
    values = list(set(df_insider["P1_IRES"].values.tolist()))
    for i in values:
        filtered = df_insider.loc[df_insider['P1_IRES']==i]
        temp_insider.loc[len(temp_insider)] = [i,filtered['Source'].values.tolist()[0],filtered['gene_name'].values.tolist()]
        
    #print(temp_insider.head())
    temp_insider = temp_insider.sort_values(by=["P1_IRES"])
    temp_insider.to_json('./templates/consolidated_insider.json', orient='records')
    return temp_insider.to_json(orient='records')

def map_phos_sites_to_insider(phos, insider):
    df_phos = pd.read_json(phos, orient='records')
    df_insider = pd.read_json(insider, orient='records')
    #df_phos['Mod'] = df_phos.Pos.map(df_insider.set_index('P1_IRES')['gene_name'].to_dict())
    df_new = df_phos[df_phos.Pos.isin(df_insider.P1_IRES)]
    df_new = df_new.replace("phos","insider")
    #df_phos = pd.merge(df_new, df_phos, how='inner')
    df_phos['Mod'] = df_phos.Pos.map(df_new.set_index('Pos')['Mod'].to_dict())
    df_phos = df_phos.fillna("phos")

    #Add identification for residues that are +-5 from an insider residue
    df_phos = proximity_mapping(df_phos,df_insider)
    df_phos.to_json('./templates/phos_selected.json', orient='records')
    return df_phos.to_json(orient='records')

def proximity_mapping(df_phos, insider):
    num_rows_phos = df_phos.shape[0]
    num_rows_insider = insider.shape[0]
    for i in range(0,num_rows_phos):
        for j in range(0,num_rows_insider):
            if (df_phos.iloc[i]["Pos"] in range(insider.iloc[j]["P1_IRES"]-5,insider.iloc[j]["P1_IRES"]+6)) and (df_phos.iloc[i]["Mod"]!="insider"):
                #df_phos.iloc[i]["Mod"] = "proximal"
                df_phos.at[i, 'Mod'] = "proximal"
                #print("Phos site proximal: ",df_phos.iloc[i]["Pos"]," first insider: ", insider.iloc[j]["P1_IRES"])
                #print(df_phos.iloc[i]["Mod"])
                break
    return df_phos

def protein_pfam_domains(uniprot_name):
    pfam_all = pd.read_csv('./data/Pfam-A_parsed_YEASTprocessed_domainAdd.txt', sep='\t')
    pfam_all.loc[pfam_all['uniprot'] == uniprot_name].to_json('./templates/pfam_selected.json',orient='records')
    return (pfam_all.loc[pfam_all['uniprot'] == uniprot_name]).to_json(orient='records')


def protein_phosphosites(uniprot_name):
    js = pd.read_csv('./data/yeast_phosphosites_parsed_2.txt', sep=',')
    js = js.loc[js['Uniprot_id'] == uniprot_name]
    #print(js.head())
    df_new = pd.DataFrame()
    df_new["uniprot"] = js["Uniprot_id"]
    pos=[]
    #Since Pos is in the weird format of number:gene at times
    #for i in range(0,js.shape[0]):
        #pos.append(int(js.iloc[i]["Pos"].split(";")[0]))

    df_new["Pos"] = js["Pos"].astype(str).str.split(";", n=1, expand=True)[0].astype(int)
    #df_new["Pos"] = pos
    #df_new["uniprot"] = js["Uniprot_id"]
    df_new["AA"] = js["AnnotatedPeptide"].str.split("(p)", n = 1, expand = True)[0].str.split("(", n = 1, expand = True)[0].str[-1:]
    df_new["Mod"] = "phos" 
    df_new["SpectralCount"] = js["#identifications"]
    df_new = df_new.sort_values(by=["Pos"])
    #print(df_new.head())
    df_new.loc[df_new['uniprot'] == uniprot_name].to_json('./templates/phos_selected.json',orient='records')
    return df_new.loc[df_new['uniprot'] == uniprot_name].to_json(orient='records')

def protein_insider_res(uniprot_name):
    insider_all = pd.read_csv('./data/S_cerevisiae_interfacesALL_2.txt', sep='\t')
    insider_all = insider_all[(insider_all['P1'] == uniprot_name) | (insider_all['P2'] == uniprot_name)]
    df_insider = pd.DataFrame(columns=list(insider_all))
    for i in range(insider_all.shape[0]):
        if insider_all.iloc[i]["P1"] == uniprot_name:
            res = insider_all.iloc[i]["P1_IRES"].strip("[").strip("]").split(',')
            for r in res:
                if "-" in r:
                    new_r = r.split('-')
                    #print(new_r[0]+1)
                    for j in range(int(new_r[0]),int(new_r[1])+1):
                        df_insider = df_insider.append({'Source': insider_all.iloc[i]['Source'], 'P1': insider_all.iloc[i]['P1'], 'P2': insider_all.iloc[i]['P2'], 'P1_IRES':j,'P2_IRES':insider_all.iloc[i]['P2_IRES']}, ignore_index=True)
                else:
                    df_insider = df_insider.append({'Source': insider_all.iloc[i]['Source'], 'P1': insider_all.iloc[i]['P1'], 'P2': insider_all.iloc[i]['P2'], 'P1_IRES':int(r),'P2_IRES':insider_all.iloc[i]['P2_IRES']}, ignore_index=True)
        else:
            res = insider_all.iloc[i]["P2_IRES"].strip("[").strip("]").split(',')
            for r in res:
                if "-" in r:
                    new_r = r.split('-')
                    #print(new_r[0]+1)
                    for j in range(int(new_r[0]),int(new_r[1])+1):
                        df_insider = df_insider.append({'Source': insider_all.iloc[i]['Source'], 'P1': insider_all.iloc[i]['P2'], 'P2': insider_all.iloc[i]['P1'], 'P1_IRES':j,'P2_IRES':insider_all.iloc[i]['P1_IRES']}, ignore_index=True)
                else:
                    df_insider = df_insider.append({'Source': insider_all.iloc[i]['Source'], 'P1': insider_all.iloc[i]['P2'], 'P2': insider_all.iloc[i]['P1'], 'P1_IRES':int(r),'P2_IRES':insider_all.iloc[i]['P1_IRES']}, ignore_index=True)            
    df_insider = df_insider.sort_values(by=["P1_IRES"])
    df_yeast_uniprottogene = pd.read_csv('./data/YEAST-uniprot-to-gene-mapping.csv', sep=',')
    df_insider['gene_name'] = df_insider.P2.map(df_yeast_uniprottogene.set_index('uniprot')['gene-name'].to_dict())
    df_insider.to_json('./templates/insider_selected.json',orient='records') 
    return df_insider.to_json(orient='records')

#protein_phosphosites("P14737")
#map_phos_sites_to_insider(protein_phosphosites("P14737"),protein_insider_res("P14737"))

#consolidate(protein_insider_res("P14737"))
if __name__ == '__main__':
    import os
    if 'WINGDB_ACTIVE' in os.environ:
        app.debug = False
    app.run(port=8001)