# main.py

from app import app
from db_setup import init_db, db_session
from forms import ProteinSearchForm
from flask import flash, render_template, request, redirect
from models import Yeast
from table import Results
#from numpy import genfromtext
import pandas as pd

#init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    search = ProteinSearchForm(request.form)
    #print("Search string: ",search)
    if request.method == 'POST':
        return search_results(search)

    return render_template('index.html', form=search)

@app.route('/download', methods=['GET', 'POST'])
def download():
    search = ProteinSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('download.html', form=search)

@app.route('/results', methods=['POST'])
def search_results(search):

    results = []
    search_string = search.data['search'].upper()
    gene_name = search_string
    
    if search_string:
        if search.data['select'] == 'Yeast':
            file_name = "./data/yeast_phosphosites_parsed_3.txt"
            data_file = pd.read_csv(file_name, delimiter=',')
            #qry = db_session.query(Yeast).filter(
                #Yeast.uniprot_id.contains(search_string))
            #results = qry.all()
            results = data_file.loc[data_file["Uniprot_id"].str.contains(search_string)]
            if results.shape[0] != 0:
                gene_name = results["Gene(s)"].values.tolist()[0]#qry.first().gene

            if results.shape[0]==0: #Check if user entered gene name instead of uniprot id
                #qry = db_session.query(Yeast).filter(
                    #Yeast.gene.contains(search_string))
                #results = qry.all()
                results = data_file.loc[data_file["Gene(s)"]==search_string]
                if results.shape[0]==0: #If the user entered neither gene name or uniprot then display error message
                    
                    flash('No results found!')
                    return redirect('/')
                else:
                    search_string = results["Uniprot_id"].values.tolist()[0]#qry.first().uniprot_id

            #for r in results:
                #if not isinstance(r.spectral_count, int):
                    #r.spectral_count = int.from_bytes(r.spectral_count,'little')
    else:
        flash('No protein entered!')
        return redirect('/')
    if results.shape[0]==0:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        prot_len_df = pd.read_csv('./data/uniprot_yeast2length.txt', sep='\t')
        prot_length = prot_len_df.loc[prot_len_df['uniprot'] == search_string]['length'].values.tolist()[0]
        print(search_string, prot_length)
        pfam_dom = protein_pfam_domains(search_string)
        phospho_sites = protein_phosphosites(search_string)
        insider = protein_insider_res(search_string)

        #Protein specific list of residues 
        pdb_pos = pdb_interfaces(insider)
        eclair_pos = eclair_interfaces(insider)
        # Separate insider sites into pdb and eclair ones
        consolidated_insider, consolidated_pos = consolidate(insider)
        # Map phos sites to insider residues to determine which ones to highlight on webpage
        phospho_sites = map_phos_sites_to_insider(phospho_sites, insider)

        table = {}#Results(results)
        #table.border = True

        # Display of phospho site information regulated
        
        return render_template('results.html', name=gene_name, pdb_interface=pdb_pos, eclair_interface=eclair_pos, pfam_table=pfam_dom, phos_table=phospho_sites, insider_table=insider, cons_insider=consolidated_insider, cons_pos=consolidated_pos, prot_len=prot_length, table=table, form=search)


###### UPDATED WEBSITE: PROTEIN SPECIFIC INTERFACE RESIDUE INFORMATION ###########################
def pdb_interfaces(insider):
    df_insider = pd.read_json(insider, orient='records')
    if (df_insider.shape[0]==0):
        return pd.DataFrame(columns=['uniprot', 'pos_list', 'gene_name']).to_json(orient='records')
    #if ("PDB" not in list(set(df_insider['Source'].values.tolist()))):
        #return pd.DataFrame(columns=['uniprot', 'pos_list', 'gene_name']).to_json(orient='records')
    
    df_insider = df_insider.loc[df_insider['Source']=='PDB']
    pos_pdb = []
    prots = list(set(df_insider['P2'].values.tolist()))
    for p in prots:
        pos_pdb.append([p, df_insider.loc[df_insider['P2']==p]['P1_IRES'].values.tolist(), df_insider.loc[df_insider['P2']==p]['gene_name'].values.tolist()[0]])
    pdb_insider = pd.DataFrame(pos_pdb, columns=['uniprot', 'pos_list', 'gene_name'])
    #pdb_insider.to_csv('./templates/pdb_pos.csv')
    return pdb_insider.to_json(orient='records')

def eclair_interfaces(insider):
    df_insider = pd.read_json(insider, orient='records')
    if (df_insider.shape[0]==0):
        return pd.DataFrame(columns=['uniprot', 'pos_list', 'gene_name']).to_json(orient='records')
    #if ("ECLAIR" not in list(set(df_insider['Source'].values.tolist()))):
        #return pd.DataFrame(columns=['uniprot', 'pos_list', 'gene_name']).to_json(orient='records')
    
    df_insider = df_insider.loc[df_insider['Source']=='ECLAIR']
    pos_eclair = []
    prots = list(set(df_insider['P2'].values.tolist()))
    for p in prots:
        pos_eclair.append([p, df_insider.loc[df_insider['P2']==p]['P1_IRES'].values.tolist(), df_insider.loc[df_insider['P2']==p]['gene_name'].values.tolist()[0]])
    eclair_insider = pd.DataFrame(pos_eclair, columns=['uniprot', 'pos_list', 'gene_name'])
    #eclair_insider.to_csv('./templates/eclair_pos.csv')
    return eclair_insider.to_json(orient='records')

##################################################################################################

def consolidate(insider):
    
    column_names = ['P1_IRES','Source','gene_name']
    temp_insider = pd.DataFrame(columns = column_names)
    temp_insider2 = pd.DataFrame(columns = column_names)
    
    df_insider = pd.read_json(insider, orient='records')
    if df_insider.shape[0]==0:
        return temp_insider.to_json(orient='records'),temp_insider2.to_json(orient='records')
    df_insider2 = df_insider.loc[df_insider['Source']=='PDB']

    values = list(set(df_insider["P1_IRES"].values.tolist()))
    values2 = list(set(df_insider2["P1_IRES"].values.tolist()))
    for i in values:
        filtered = df_insider.loc[df_insider['P1_IRES']==i]
        temp_insider.loc[len(temp_insider)] = [i,filtered['Source'].values.tolist(),filtered['gene_name'].values.tolist()]
        
    for i in values2:
        filtered2 = df_insider2.loc[df_insider2['P1_IRES']==i]
        temp_insider2.loc[len(temp_insider2)] = [i,filtered2['Source'].values.tolist(),filtered2['gene_name'].values.tolist()]
    
    temp_insider = temp_insider.sort_values(by=["P1_IRES"])
    temp_insider2 = temp_insider2.sort_values(by=["P1_IRES"])

    #temp_insider.to_json('./templates/consolidated_insider.json', orient='records')
    #temp_insider.to_csv('./templates/consolidated_interfaces.txt', sep='\t')
    #temp_insider.to_csv('./templates/consolidated_interfaces.csv')

    #temp_insider2.to_csv('./templates/consolidated_pos.csv')
    return temp_insider.to_json(orient='records'),temp_insider2.to_json(orient='records')

def map_phos_sites_to_insider(phos, insider):
    df_phos = pd.read_json(phos, orient='records')
    df_insider = pd.read_json(insider, orient='records')
    #df_phos['Mod'] = df_phos.Pos.map(df_insider.set_index('P1_IRES')['gene_name'].to_dict())
    if df_insider.shape[0]==0:
        df_phos["Mod"] = "phos"
        return df_phos.to_json(orient='records')
    df_new = df_phos[df_phos.Pos.isin(df_insider.P1_IRES)]
    df_new = df_new.replace("phos","insider")
    #df_phos = pd.merge(df_new, df_phos, how='inner')
    df_phos['Mod'] = df_phos.Pos.map(df_new.set_index('Pos')['Mod'].to_dict())
    df_phos = df_phos.fillna("phos")

    #Add identification for residues that are +-5 from an insider residue
    df_phos = proximity_mapping(df_phos,df_insider)
    #df_phos.to_json('./templates/phos_selected.json', orient='records')
    return df_phos.to_json(orient='records')

def proximity_mapping(df_phos, insider):
    num_rows_phos = df_phos.shape[0]
    num_rows_insider = insider.shape[0]
    for i in range(0,num_rows_phos):
        for j in range(0,num_rows_insider):
            if (df_phos.iloc[i]["Pos"] in range(insider.iloc[j]["P1_IRES"]-5,insider.iloc[j]["P1_IRES"]+6)) and (df_phos.iloc[i]["Mod"]!="insider"):
                #df_phos.iloc[i]["Mod"] = "proximal"
                df_phos.at[i, 'Mod'] = "proximal"
                break
    return df_phos

def protein_pfam_domains(uniprot_name):
    pfam_all = pd.read_csv('./data/Pfam-A_parsed_YEASTprocessed_domainAdd.txt', sep='\t')
    pfam_all.loc[pfam_all['uniprot'] == uniprot_name].to_json('./templates/pfam_selected.json',orient='records')
    return (pfam_all.loc[pfam_all['uniprot'] == uniprot_name]).to_json(orient='records')


def protein_phosphosites(uniprot_name):
    js = pd.read_csv('./data/yeast_phosphosites_parsed_3.txt', sep=',')
    js = js.loc[js['Uniprot_id'] == uniprot_name]
    
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
                    
                    for j in range(int(new_r[0]),int(new_r[1])+1):
                        df_insider = df_insider.append({'Source': insider_all.iloc[i]['Source'], 'P1': insider_all.iloc[i]['P1'], 'P2': insider_all.iloc[i]['P2'], 'P1_IRES':j,'P2_IRES':insider_all.iloc[i]['P2_IRES']}, ignore_index=True)
                else:
                    df_insider = df_insider.append({'Source': insider_all.iloc[i]['Source'], 'P1': insider_all.iloc[i]['P1'], 'P2': insider_all.iloc[i]['P2'], 'P1_IRES':int(r),'P2_IRES':insider_all.iloc[i]['P2_IRES']}, ignore_index=True)
        else:
            res = insider_all.iloc[i]["P2_IRES"].strip("[").strip("]").split(',')
            for r in res:
                if "-" in r:
                    new_r = r.split('-')
                    
                    for j in range(int(new_r[0]),int(new_r[1])+1):
                        df_insider = df_insider.append({'Source': insider_all.iloc[i]['Source'], 'P1': insider_all.iloc[i]['P2'], 'P2': insider_all.iloc[i]['P1'], 'P1_IRES':j,'P2_IRES':insider_all.iloc[i]['P1_IRES']}, ignore_index=True)
                else:
                    df_insider = df_insider.append({'Source': insider_all.iloc[i]['Source'], 'P1': insider_all.iloc[i]['P2'], 'P2': insider_all.iloc[i]['P1'], 'P1_IRES':int(r),'P2_IRES':insider_all.iloc[i]['P1_IRES']}, ignore_index=True)            
    df_insider = df_insider.sort_values(by=["P1_IRES"])
    df_yeast_uniprottogene = pd.read_csv('./data/YEAST-uniprot-to-gene-mapping.csv', sep=',')
    df_insider['gene_name'] = df_insider.P2.map(df_yeast_uniprottogene.set_index('uniprot')['gene-name'].to_dict())
    #df_insider.to_json('./templates/insider_selected.json',orient='records') 
    return df_insider.to_json(orient='records')

#protein_phosphosites("P14737")
#map_phos_sites_to_insider(protein_phosphosites("P14737"),protein_insider_res("P14737"))

#consolidate(protein_insider_res("P14737"))
if __name__ == '__main__':
    import os
    if 'WINGDB_ACTIVE' in os.environ:
        app.debug = False
    app.run(port=8967)