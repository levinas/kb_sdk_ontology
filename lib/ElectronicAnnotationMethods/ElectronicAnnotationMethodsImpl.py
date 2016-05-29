#BEGIN_HEADER
# The header block is where all import statments should live
import csv
import os
import re
import subprocess
import sys
import time
import traceback
import uuid
from pprint import pprint, pformat
from biokbase.workspace.client import Workspace as workspaceService

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
#END_HEADER


class ElectronicAnnotationMethods:
    '''
    Module Name:
    ElectronicAnnotationMethods

    Module Description:
    A KBase module: ElectronicAnnotationMethods
This module wraps the following methods:

  interpro2go          -> InterPro2GO
  ec2go                -> EC2GO
  uniprotkb_keyword2go -> UniProtKB-Keyword2GO
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    #BEGIN_CLASS_HEADER
    # Class variables and functions can be defined in this block
    workspaceURL = None

    def genome_to_protein_fasta(self, genome, fasta_file):
        records = []
        for feature in genome['features']:
            record = SeqRecord(Seq(feature['protein_translation']),
                               id=feature['id'], description=feature['function'])
            records.append(record)
        SeqIO.write(records, fasta_file, "fasta")

    def uniq_seen(self, iterable):
        seen = set()
        seen_add = seen.add
        return [x for x in iterable if not (x in seen or seen_add(x))]

    def equiv_term_to_string(self, x):
        s = x['equiv_term']
        if 'equiv_name' in x:
            name = x['equiv_name']
            s += ' ' + re.sub(r'^GO:', '', name)
        return s

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        self.scratch = os.path.abspath(config['scratch'])
        if not os.path.exists(self.scratch):
            os.makedirs(self.scratch)
        #END_CONSTRUCTOR
        pass

    def remap_annotations_with_interpro2go(self, ctx, params):
        # ctx is the context object
        # return variables are: output
        #BEGIN remap_annotations_with_interpro2go

        # Print statements to stdout/stderr are captured and available as the method log
        print('Starting remap_annotations_with_interpro2go method...')


        # Step 1 - Parse/examine the parameters and catch any errors
        # It is important to check that parameters exist and are defined, and that nice error
        # messages are returned to the user
        if 'workspace' not in params:
            raise ValueError('Parameter workspace is not set in input arguments')
        workspace_name = params['workspace']

        if 'input_genome' not in params:
            raise ValueError('Parameter input_genome is not set in input arguments')
        input_genome = params['input_genome']

        if 'output_genome' not in params:
            raise ValueError('Parameter output_genome is not set in input arguments')
        output_genome = params['output_genome']

        ontology_translation = params.get('ontology_translation')


        # Step 2- Download the input data
        # Most data will be based to your method by its workspace name.  Use the workspace to pull that data
        # (or in many cases, subsets of that data).  The user token is used to authenticate with the KBase
        # data stores and other services.  DO NOT PRINT OUT OR OTHERWISE SAVE USER TOKENS
        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        try:
            # Note that results from the workspace are returned in a list, and the actual data is saved
            # in the 'data' key.  So to get the ContigSet data, we get the first element of the list, and
            # look at the 'data' field.
            genome = wsClient.get_objects([{'ref': workspace_name+'/'+input_genome}])[0]['data']
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error loading input Genome object from workspace:\n' + orig_error)

        print('Got input genome data.')

        # Load translation object from default or user-specified table
        translation_ws = workspace_name
        translation_name = ontology_translation
        if not translation_name:
            translation_ws = 'KBaseOntology'
            translation_name = 'interpro2go'
        try:
            translation = wsClient.get_objects([{'ref': translation_ws+'/'+translation_name}])[0]['data']
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error loading OntologyTranslation object from workspace:\n' + orig_error)

        trans = translation['translation']
        print('Got translation table from {}/{}.'.format(translation_ws, translation_name))

        # Step 3- Actually perform the interpro2go mapping operation

        # Create feature protein FASTA as input for interproscan
        fasta_path = os.path.join(self.scratch, 'protein.fa')
        interpro_out = os.path.join(self.scratch, 'protein.tsv')
        self.genome_to_protein_fasta(genome, fasta_path)

        # Check java version
        subprocess.call("which java", shell=True)
        subprocess.call("type -p java", shell=True)
        subprocess.call("ls -ltr /kb/runtime/bin/java", shell=True)
        subprocess.call("ls -ltr /etc/alternatives/java", shell=True)
        subprocess.call("/kb/runtime/bin/java -version", shell=True)
        subprocess.call("/etc/alternatives/java -version", shell=True)
        subprocess.call("ls -ltr /usr/lib/jvm", shell=True)

        # Run interproscan in standalone mode
        cmd = ['interproscan.sh',
               '-i', fasta_path,
               '-f', 'tsv',
               '-o', interpro_out,
               '--disable-precalc',
               '-goterms',
               '-iprlookup', '-hm' ]

        print('Run CMD: {}'.format(' '.join(cmd)))
        p = subprocess.Popen(cmd, cwd = self.scratch, shell = False)
        p.wait()
        print('CMD return code: {}'.format(p.returncode))

        # Add GO terms to Genome object
        fid_to_go = {}
        with open(interpro_out, 'r') as tsv:
            tsv = csv.reader(tsv, delimiter='\t')
            for row in tsv:
                if len(row) < 12:
                    continue
                fid, beg, end, domain = row[0], row[6], row[7], row[11]
                # orig_go_terms = None
                # if len(row) >= 14:
                    # orig_go_terms = row[13]
                go_terms = None
                key = 'InterPro:'+domain
                equiv_terms = trans.get(key)
                if equiv_terms:
                    go_terms = '|'.join(sorted(map(lambda x: x['equiv_term'], equiv_terms['equiv_terms'])))
                    fid_to_go[fid] = go_terms

        n_total_features = 0
        n_features_mapped = 0
        for fea in genome['features']:
            fid = fea['id']
            n_total_features += 1
            if fid in fid_to_go:
                anno = fea['annotations'] if 'annotations' in fea else []
                anno.append([fid_to_go[fid], 'interpro2go', int(time.time())])
                n_features_mapped += 1
                print('Mapped {} to {}.'.format(fid, fid_to_go[fid]))

        # Step 4- Save the new Genome back to the Workspace
        # When objects are saved, it is important to always set the Provenance of that object.  The basic
        # provenance info is given to you as part of the context object.  You can add additional information
        # to the provenance as necessary.  Here we keep a pointer to the input data object.
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects']=[workspace_name+'/'+input_genome]

        obj_info_list = None
        try:
	        obj_info_list = wsClient.save_objects({
	                            'workspace':workspace_name,
	                            'objects': [
	                                {
	                                    'type':'KBaseGenomes.Genome',
	                                    'data':genome,
	                                    'name':output_genome,
	                                    'provenance':provenance
	                                }
	                            ]
	                        })
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error saving output Genome object to workspace:\n' + orig_error)

        info = obj_info_list[0]
        # Workspace Object Info is a tuple defined as-
        # absolute ref = info[6] + '/' + info[0] + '/' + info[4]
        # 0 - obj_id objid - integer valued ID of the object
        # 1 - obj_name name - the name of the data object
        # 2 - type_string type - the full type of the data object as: [ModuleName].[Type]-v[major_ver].[minor_ver]
        # 3 - timestamp save_date
        # 4 - int version - the object version number
        # 5 - username saved_by
        # 6 - ws_id wsid - the unique integer valued ID of the workspace containing this object
        # 7 - ws_name workspace - the workspace name
        # 8 - string chsum - md5 of the sorted json content
        # 9 - int size - size of the json content
        # 10 - usermeta meta - dictionary of string keys/values of user set or auto generated metadata

        print('Saved output Genome:'+pformat(info))


        # Step 5- Create the Report for this method, and return the results
        # Create a Report of the method
        report = 'New Genome saved to: '+str(info[7]) + '/'+str(info[1])+'/'+str(info[4])+'\n'
        report += 'Number of total features: '+ str(n_total_features) + '\n'
        report += 'Number of features mapped to GO terms: '+ str(n_features_mapped) + '\n'

        reportObj = {
            'objects_created':[{
                    'ref':str(info[6]) + '/'+str(info[0])+'/'+str(info[4]),
                    'description':'Genome with annotation remapped using interpro2go'
                }],
            'text_message':report
        }

        # generate a unique name for the Method report
        reportName = 'interpro2go_report_'+str(hex(uuid.getnode()))
        report_info_list = None
        try:
            report_info_list = wsClient.save_objects({
                    'id':info[6],
                    'objects':[
                        {
                            'type':'KBaseReport.Report',
                            'data':reportObj,
                            'name':reportName,
                            'meta':{},
                            'hidden':1, # important!  make sure the report is hidden
                            'provenance':provenance
                        }
                    ]
                })
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error saving report object to workspace:\n' + orig_error)

        report_info = report_info_list[0]

        print('Saved Report: '+pformat(report_info))

        output = {
                'report_name': reportName,
                'report_ref': str(report_info[6]) + '/' + str(report_info[0]) + '/' + str(report_info[4]),
                'output_genome_ref': str(info[6]) + '/'+str(info[0])+'/'+str(info[4]),
                'n_total_features':n_total_features,
                'n_features_mapped':n_features_mapped
            }

        print('Returning: '+pformat(output))

        #END remap_annotations_with_interpro2go

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method remap_annotations_with_interpro2go return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def remap_annotations_with_ec2go(self, ctx, params):
        # ctx is the context object
        # return variables are: output
        #BEGIN remap_annotations_with_ec2go

        # Print statements to stdout/stderr are captured and available as the method log
        print('Starting remap_annotations_with_ec2go method...')

        # Step 1 - Parse/examine the parameters and catch any errors
        # It is important to check that parameters exist and are defined, and that nice error
        # messages are returned to the user
        if 'workspace' not in params:
            raise ValueError('Parameter workspace is not set in input arguments')
        workspace_name = params['workspace']

        if 'input_genome' not in params:
            raise ValueError('Parameter input_genome is not set in input arguments')
        input_genome = params['input_genome']

        if 'output_genome' not in params:
            raise ValueError('Parameter output_genome is not set in input arguments')
        output_genome = params['output_genome']

        ontology_translation = params.get('ontology_translation')

        # Step 2- Download the input data
        # Most data will be based to your method by its workspace name.  Use the workspace to pull that data
        # (or in many cases, subsets of that data).  The user token is used to authenticate with the KBase
        # data stores and other services.  DO NOT PRINT OUT OR OTHERWISE SAVE USER TOKENS
        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        try:
            # Note that results from the workspace are returned in a list, and the actual data is saved
            # in the 'data' key.  So to get the ContigSet data, we get the first element of the list, and
            # look at the 'data' field.
            genome = wsClient.get_objects([{'ref': workspace_name+'/'+input_genome}])[0]['data']
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error loading input Genome object from workspace:\n' + orig_error)

        print('Got input genome data.')

        # Load translation object from default or user-specified table
        translation_ws = workspace_name
        translation_name = ontology_translation
        if not translation_name:
            translation_ws = 'KBaseOntology'
            translation_name = 'ec2go'
        try:
            translation = wsClient.get_objects([{'ref': translation_ws+'/'+translation_name}])[0]['data']
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error loading OntologyTranslation object from workspace:\n' + orig_error)

        trans = translation['translation']
        print('Got translation table from {}/{}.'.format(translation_ws, translation_name))

        # Step 3- Actually perform the ec2go mapping operation

        # Add GO terms to Genome object
        # print trans
        n_total_features = 0
        n_features_mapped = 0
        for fea in genome['features']:
            n_total_features += 1
            fid = fea['id']
            function = fea.get('function')
            if not function:
                continue
            matches = re.findall('EC[ :][-0-9]+\.[-0-9]+\.[-0-9]+\.[-0-9]+', function)
            ec_list = self.uniq_seen(matches)
            go_list = []
            for ec in ec_list:
                key = ec.replace("EC ", "EC:")
                equiv_terms = trans.get(key)
                if equiv_terms:
                    go = map(lambda x: self.equiv_term_to_string(x), equiv_terms['equiv_terms'])
                    go_list.extend(go)
            if len(go_list):
                n_features_mapped += 1
                go_func = ' / '.join(sorted(go_list))
                fea['function'] = go_func
                print('Mapped {} from "{}"to "{}".'.format(fid, function, go_func))


        # Step 4- Save the new Genome back to the Workspace
        # When objects are saved, it is important to always set the Provenance of that object.  The basic
        # provenance info is given to you as part of the context object.  You can add additional information
        # to the provenance as necessary.  Here we keep a pointer to the input data object.
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects']=[workspace_name+'/'+input_genome]

        obj_info_list = None
        try:
	        obj_info_list = wsClient.save_objects({
	                            'workspace':workspace_name,
	                            'objects': [
	                                {
	                                    'type':'KBaseGenomes.Genome',
	                                    'data':genome,
	                                    'name':output_genome,
	                                    'provenance':provenance
	                                }
	                            ]
	                        })
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error saving output Genome object to workspace:\n' + orig_error)

        info = obj_info_list[0]
        # Workspace Object Info is a tuple defined as-
        # absolute ref = info[6] + '/' + info[0] + '/' + info[4]
        # 0 - obj_id objid - integer valued ID of the object
        # 1 - obj_name name - the name of the data object
        # 2 - type_string type - the full type of the data object as: [ModuleName].[Type]-v[major_ver].[minor_ver]
        # 3 - timestamp save_date
        # 4 - int version - the object version number
        # 5 - username saved_by
        # 6 - ws_id wsid - the unique integer valued ID of the workspace containing this object
        # 7 - ws_name workspace - the workspace name
        # 8 - string chsum - md5 of the sorted json content
        # 9 - int size - size of the json content
        # 10 - usermeta meta - dictionary of string keys/values of user set or auto generated metadata

        print('Saved output Genome:'+pformat(info))


        # Step 5- Create the Report for this method, and return the results
        # Create a Report of the method
        report = 'New Genome saved to: '+str(info[7]) + '/'+str(info[1])+'/'+str(info[4])+'\n'
        report += 'Number of total features: '+ str(n_total_features) + '\n'
        report += 'Number of features mapped to GO terms: '+ str(n_features_mapped) + '\n'

        reportObj = {
            'objects_created':[{
                    'ref':str(info[6]) + '/'+str(info[0])+'/'+str(info[4]),
                    'description':'Genome with annotation remapped using ec2go'
                }],
            'text_message':report
        }

        # generate a unique name for the Method report
        reportName = 'ec2go_report_'+str(hex(uuid.getnode()))
        report_info_list = None
        try:
            report_info_list = wsClient.save_objects({
                    'id':info[6],
                    'objects':[
                        {
                            'type':'KBaseReport.Report',
                            'data':reportObj,
                            'name':reportName,
                            'meta':{},
                            'hidden':1, # important!  make sure the report is hidden
                            'provenance':provenance
                        }
                    ]
                })
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error saving report object to workspace:\n' + orig_error)

        report_info = report_info_list[0]

        print('Saved Report: '+pformat(report_info))

        output = {
                'report_name': reportName,
                'report_ref': str(report_info[6]) + '/' + str(report_info[0]) + '/' + str(report_info[4]),
                'output_genome_ref': str(info[6]) + '/'+str(info[0])+'/'+str(info[4]),
                'n_total_features':n_total_features,
                'n_features_mapped':n_features_mapped
            }

        print('Returning: '+pformat(output))

        #END remap_annotations_with_ec2go

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method remap_annotations_with_ec2go return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def remap_annotations_with_uniprotkb_keyword2go(self, ctx, params):
        # ctx is the context object
        # return variables are: output
        #BEGIN remap_annotations_with_uniprotkb_keyword2go

        # Print statements to stdout/stderr are captured and available as the method log
        print('Starting remap_annotations_with_uniprotkb_keyword2go method...')

        # Step 1 - Parse/examine the parameters and catch any errors
        # It is important to check that parameters exist and are defined, and that nice error
        # messages are returned to the user
        if 'workspace' not in params:
            raise ValueError('Parameter workspace is not set in input arguments')
        workspace_name = params['workspace']

        if 'input_genome' not in params:
            raise ValueError('Parameter input_genome is not set in input arguments')
        input_genome = params['input_genome']

        if 'output_genome' not in params:
            raise ValueError('Parameter output_genome is not set in input arguments')
        output_genome = params['output_genome']

        ontology_translation = params.get('ontology_translation')

        # Step 2- Download the input data
        # Most data will be based to your method by its workspace name.  Use the workspace to pull that data
        # (or in many cases, subsets of that data).  The user token is used to authenticate with the KBase
        # data stores and other services.  DO NOT PRINT OUT OR OTHERWISE SAVE USER TOKENS
        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        try:
            # Note that results from the workspace are returned in a list, and the actual data is saved
            # in the 'data' key.  So to get the ContigSet data, we get the first element of the list, and
            # look at the 'data' field.
            genome = wsClient.get_objects([{'ref': workspace_name+'/'+input_genome}])[0]['data']
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error loading input Genome object from workspace:\n' + orig_error)

        print('Got input genome data.')

        # Load translation object from default or user-specified table
        translation_ws = workspace_name
        translation_name = ontology_translation
        if not translation_name:
            translation_ws = 'KBaseOntology'
            translation_name = 'uniprotkb_kw2go'
        try:
            translation = wsClient.get_objects([{'ref': translation_ws+'/'+translation_name}])[0]['data']
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error loading OntologyTranslation object from workspace:\n' + orig_error)

        trans = translation['translation']
        print('Got translation table from {}/{}.'.format(translation_ws, translation_name))

        # Step 3- Actually perform the uniprotkb_keyword2go mapping operation

        # Add GO terms to Genome object
        # print trans
        n_total_features = 0
        n_features_mapped = 0
        for fea in genome['features']:
            n_total_features += 1
            fid = fea['id']
            function = fea.get('function')
            if not function:
                continue
            go_list = []
            for term in trans.keys():
                keyword = trans[term]['name']
                if function.lower().find(keyword.lower()) >= 0:
                    equiv_terms = trans.get(term)
                    if equiv_terms:
                        go = map(lambda x: self.equiv_term_to_string(x), equiv_terms['equiv_terms'])
                        go_list.extend(go)
            go_list = self.uniq_seen(go_list)
            if len(go_list):
                n_features_mapped += 1
                go_func = ' / '.join(sorted(go_list))
                fea['function'] = go_func
                print('Mapped {} from "{}"to "{}".'.format(fid, function, go_func))


        # Step 4- Save the new Genome back to the Workspace
        # When objects are saved, it is important to always set the Provenance of that object.  The basic
        # provenance info is given to you as part of the context object.  You can add additional information
        # to the provenance as necessary.  Here we keep a pointer to the input data object.
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]['input_ws_objects']=[workspace_name+'/'+input_genome]

        obj_info_list = None
        try:
	        obj_info_list = wsClient.save_objects({
	                            'workspace':workspace_name,
	                            'objects': [
	                                {
	                                    'type':'KBaseGenomes.Genome',
	                                    'data':genome,
	                                    'name':output_genome,
	                                    'provenance':provenance
	                                }
	                            ]
	                        })
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error saving output Genome object to workspace:\n' + orig_error)

        info = obj_info_list[0]
        # Workspace Object Info is a tuple defined as-
        # absolute ref = info[6] + '/' + info[0] + '/' + info[4]
        # 0 - obj_id objid - integer valued ID of the object
        # 1 - obj_name name - the name of the data object
        # 2 - type_string type - the full type of the data object as: [ModuleName].[Type]-v[major_ver].[minor_ver]
        # 3 - timestamp save_date
        # 4 - int version - the object version number
        # 5 - username saved_by
        # 6 - ws_id wsid - the unique integer valued ID of the workspace containing this object
        # 7 - ws_name workspace - the workspace name
        # 8 - string chsum - md5 of the sorted json content
        # 9 - int size - size of the json content
        # 10 - usermeta meta - dictionary of string keys/values of user set or auto generated metadata

        print('Saved output Genome:'+pformat(info))


        # Step 5- Create the Report for this method, and return the results
        # Create a Report of the method
        report = 'New Genome saved to: '+str(info[7]) + '/'+str(info[1])+'/'+str(info[4])+'\n'
        report += 'Number of total features: '+ str(n_total_features) + '\n'
        report += 'Number of features mapped to GO terms: '+ str(n_features_mapped) + '\n'

        reportObj = {
            'objects_created':[{
                    'ref':str(info[6]) + '/'+str(info[0])+'/'+str(info[4]),
                    'description':'Genome with annotation remapped using uniprotkb_keyword2go'
                }],
            'text_message':report
        }

        # generate a unique name for the Method report
        reportName = 'uniprotkb_keyword2go_report_'+str(hex(uuid.getnode()))
        report_info_list = None
        try:
            report_info_list = wsClient.save_objects({
                    'id':info[6],
                    'objects':[
                        {
                            'type':'KBaseReport.Report',
                            'data':reportObj,
                            'name':reportName,
                            'meta':{},
                            'hidden':1, # important!  make sure the report is hidden
                            'provenance':provenance
                        }
                    ]
                })
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error saving report object to workspace:\n' + orig_error)

        report_info = report_info_list[0]

        print('Saved Report: '+pformat(report_info))

        output = {
                'report_name': reportName,
                'report_ref': str(report_info[6]) + '/' + str(report_info[0]) + '/' + str(report_info[4]),
                'output_genome_ref': str(info[6]) + '/'+str(info[0])+'/'+str(info[4]),
                'n_total_features':n_total_features,
                'n_features_mapped':n_features_mapped
            }

        print('Returning: '+pformat(output))

        #END remap_annotations_with_uniprotkb_keyword2go

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method remap_annotations_with_uniprotkb_keyword2go return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
