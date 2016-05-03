import unittest
import os
import json
import time

from os import environ
from ConfigParser import ConfigParser
from pprint import pprint

from biokbase.workspace.client import Workspace as workspaceService
from ElectronicAnnotationMethods.ElectronicAnnotationMethodsImpl import ElectronicAnnotationMethods


class ElectronicAnnotationMethodsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        cls.ctx = {'token': token, 'provenance': [{'service': 'ElectronicAnnotationMethods',
            'method': 'please_never_use_it_in_production', 'method_params': []}],
            'authenticated': 1}
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('ElectronicAnnotationMethods'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        print cls.wsURL
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = ElectronicAnnotationMethods(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_ElectronicAnnotationMethods_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx
        
#    def test_interpro2go_ok(self):
#        input_name = "genome.1"
#        output_name = "out.genome.1.interpro2go"
#        obj = self.get_test_genome_1()
#        workspace = self.getWsName()
#        self.getWsClient().save_objects({'workspace': workspace, 'objects':
#                                         [{'type': 'KBaseGenomes.Genome', 'name': input_name, 'data': obj}]})
#        ret = self.getImpl().remap_annotations_with_interpro2go(self.getContext(),
#                                                                {'workspace': workspace,
#                                                                 'input_genome': input_name, 'output_genome': output_name})
#        new_obj = self.getWsClient().get_objects([{'ref': workspace+'/'+output_name}])[0]['data']
#        print new_obj

        # contig1 = {'id': '1', 'length': 10, 'md5': 'md5', 'sequence': 'agcttttcat'}
        # contig2 = {'id': '2', 'length': 5, 'md5': 'md5', 'sequence': 'agctt'}
        # contig3 = {'id': '3', 'length': 12, 'md5': 'md5', 'sequence': 'agcttttcatgg'}
        # obj1 = {'contigs': [contig1, contig2, contig3], 'id': 'id', 'md5': 'md5', 'name': 'name',
        #         'source': 'source', 'source_id': 'source_id', 'type': 'type'}
        # self.getWsClient().save_objects({'workspace': self.getWsName(), 'objects':
        #     [{'type': 'KBaseGenomes.ContigSet', 'name': obj_name, 'data': obj1}]})
        # ret = self.getImpl().filter_contigs(self.getContext(), {'workspace': self.getWsName(),
        #     'contigset_id': obj_name, 'min_length': '10'})
        # obj2 = self.getWsClient().get_objects([{'ref': self.getWsName()+'/'+obj_name}])[0]['data']
        # self.assertEqual(len(obj2['contigs']), 2)
        # self.assertTrue(len(obj2['contigs'][0]['sequence']) >= 10)
        # self.assertTrue(len(obj2['contigs'][1]['sequence']) >= 10)
        # self.assertEqual(ret[0]['n_initial_contigs'], 3)
        # self.assertEqual(ret[0]['n_contigs_removed'], 1)
        # self.assertEqual(ret[0]['n_contigs_remaining'], 2)


#    def test_ec2go_ok(self):
#        input_name = "genome.1"
#        output_name = "out.genome.1.ec2go"
#        obj = self.get_test_genome_1()
#        workspace = self.getWsName()
#        self.getWsClient().save_objects({'workspace': workspace, 'objects':
#                                         [{'type': 'KBaseGenomes.Genome', 'name': input_name, 'data': obj}]})
#        ret = self.getImpl().remap_annotations_with_ec2go(self.getContext(),
#                                                          {'workspace': workspace,
#                                                           'input_genome': input_name, 'output_genome': output_name})
#        new_obj = self.getWsClient().get_objects([{'ref': workspace+'/'+output_name}])[0]['data']
#        print new_obj
    
    def test_uniprotkb_keyword2go_ok(self):
        input_name = "genome.1"
        output_name = "out.genome.1.uniprotkb_keyword2go"
        obj = self.get_test_genome_1()
        workspace = self.getWsName()
        self.getWsClient().save_objects({'workspace': workspace, 'objects':
                                         [{'type': 'KBaseGenomes.Genome', 'name': input_name, 'data': obj}]})
        ret = self.getImpl().remap_annotations_with_ec2go(self.getContext(),
                                                          {'workspace': workspace,
                                                           'input_genome': input_name, 'output_genome': output_name})
        new_obj = self.getWsClient().get_objects([{'ref': workspace+'/'+output_name}])[0]['data']
        print new_obj

    def get_test_genome_1(self):
        obj_json = '''
{
    "complete": 0,
    "contig_ids": [
        "kb|g.960.c.1",
        "kb|g.960.c.2"
    ],
    "contig_lengths": [
        3768,
        4083
    ],
    "dna_size": 5206906,
    "domain": "Bacteria",
    "features": [
        {
            "aliases": [
                "ZP_00721180.1",
                "EcolF_01003998",
                "75237130",
                "COG2207",
                "2458280"
            ],
            "annotations": [
                [
                    "Multiple antibiotic resistance protein MarA",
                    "claudia",
                    1200689353
                ],
                [
                    "Set function to COG4776: Exoribonuclease II",
                    "ncbi",
                    1149627647
                ],
                [
                    "Set function to Multiple antibiotic resistance protein MarA",
                    "claudia",
                    1200689353
                ]
            ],
            "co_occurring_fids": [
                [
                    "kb|g.960.peg.3078",
                    33
                ],
                [
                    "kb|g.960.peg.3442",
                    6
                ],
                [
                    "kb|g.960.peg.3495",
                    5
                ],
                [
                    "kb|g.960.peg.3756",
                    6
                ],
                [
                    "kb|g.960.peg.3890",
                    7
                ]
            ],
            "dna_sequence": "atgacgatgtccagacgcaatactgacgctattaccattcatagcattttggactggatcgaggacaacctggaatcgccactttcactggagaaagtgtcagagcgttcgggttactccaaatggcacctgcaacggatgtttaaaaaagaaaccggtcattcattaggtcaatacatccgtagccgtaagatgacggaaatcgcgcaaaagctgaaggaaagtaacgagccgatactctatctggcagaacgatatggctttgagtcccaacaaactctgacccgaaccttcaaaaattactttgatgttccgccgcataaataccggatgaccaatatgcaaggtgaatcgcgttttttacatccattaaatcattacaacaactag",
            "dna_sequence_length": 390,
            "function": "Multiple antibiotic resistance protein MarA",
            "id": "kb|g.960.peg.3275",
            "location": [
                [
                    "kb|g.960.c.3",
                    11339,
                    "-",
                    390
                ]
            ],
            "md5": "45a87821a445ae8b2a8c436a1aae94e1",
            "protein_families": [
                {
                    "id": "FIG00004085",
                    "release_version": "Release59",
                    "subject_db": "FIGfam",
                    "subject_description": "Multiple antibiotic resistance protein MarA"
                }
            ],
            "protein_translation": "MTMSRRNTDAITIHSILDWIEDNLESPLSLEKVSERSGYSKWHLQRMFKKETGHSLGQYIRSRKMTEIAQKLKESNEPILYLAERYGFESQQTLTRTFKNYFDVPPHKYRMTNMQGESRFLHPLNHYNN",
            "protein_translation_length": 129,
            "type": "CDS"
        },
        {
            "aliases": [
                "ZP_00724853.1",
                "EcolF_01002034",
                "75240964",
                "COG4988",
                "2456354"
            ],
            "annotations": [
                [
                    "Function set by OlgaV at 1233268189 Transport ATP-binding protein CydD",
                    "OlgaV",
                    1233268189
                ],
                [
                    "Role changed from 'Transport ATP-binding protein cydD' to 'Transport ATP-binding protein CydD'",
                    "OlgaV",
                    1233268189
                ],
                [
                    "Set function to hypothetical protein",
                    "ncbi",
                    1149627647
                ],
                [
                    "Set function to Transport ATP-binding protein CydD",
                    "OlgaV",
                    1233268189
                ]
            ],
            "co_occurring_fids": [
                [
                    "kb|g.960.peg.1088",
                    31
                ],
                [
                    "kb|g.960.peg.1187",
                    21
                ],
                [
                    "kb|g.960.peg.1489",
                    15
                ],
                [
                    "kb|g.960.peg.1528",
                    37
                ],
                [
                    "kb|g.960.peg.1550",
                    22
                ],
                [
                    "kb|g.960.peg.1794",
                    145
                ],
                [
                    "kb|g.960.peg.1904",
                    21
                ]
            ],
            "dna_sequence": "atgaataaatcccgtcaaaaagaattaacccgctggttaaaacagcaaagcgtcatctcccaacgttggctgaatatttctcgtctgctgggctttgtgagcggcatattgatcattgcccaggcctggttcatggcgcgaattctgcaacatatgattatggagaatattccccgtgaagccctgctgcttccctttacgttactgtttctgacctttgtactgcgcgcatgggtggtctggttacgcgaacgggtgggttatcacgccgggcagcatatccgctttgccatccgccgtcaggttctcgaccgtctgcaacaagcagggccagcgtggattcagggtaaacctgcggggagctgggcgacgctggtgctcgagcaaattgacgatatgcatgattactatgcacgctacctgccgcaaatggcgctggcagtgtcggtgccgctgctgattgtggtggctatcttcccctctaactgggctgcggcgctcattctgctgggcactgcaccgctaattccgttatttatggcgctggttggaatgggggctgccgatgctaaccgacgtaactttctcgctcttgctcgcttaagtgggcatttcctcgatcgcctgcgcggcatggaaacattgcgtatttttggtcgtggtgaagctgaaattgaaagtattcgttctgcttcggaagatttccgccaacggacaatggaagtgctacggctggcgtttttatcctccggcattctcgaattttttacctcgctgtcgattgctctggtggcgatctactttggtttttcctacctcggcgagctggattttggtcactacgatactggtgtgacgctggctgcgggttttctagccctgatccttgcgccagagtttttccagccattacgcgatctcggtacgttttatcatgctaaagcccaggctgttggtgcagctgacagtttgaaaacgtttatggaaaccccgctcgcccatccgcagcgcggtgaggcggaattagcatcgaccgatccggtgaccattgaagccgaggatctgtttatcacgtcgccggaaggtaaaacgctggccggaccgctgaattttactttgccagcaggccaacgagcagtgttggttggtcgcagcggttcaggtaaaagttcactgttgaacgcgctttctggttttctctcatatcagggatcgctacgaatcaacgggatagaattacgcgatttatcaccggaatcatggcgtaaacatctctcctgggttgggcaaaacccacaattaccggcagcaacattacgggataacgtactactggcgcgacctgatgccagcgaacaagagttacaaacagcgctggataacgcctgggtcagtgagtttctaccgctcctgccgcaaggcattgatacgcctgttggtgaccaggctgcccgcctttccgtggggcaggcgcagcgcgtggcggtggcccgtgcgttactaaatccctgttcgctattactgttggatgaacccgctgccagccttgatgctcacagtgaacagcgcgtaatggaggcgctgaatgccgcctctctgcgccagacaacgttaatggtcacccaccagttagaagatcttgctgactgggatgtcatttgggtaatgcaggatggtcagattattgagcaaggacgttacgcggaattaagtgtggctggcggcccattcgccacattactggcccatcgtcaggaggagatttaa",
            "dna_sequence_length": 1767,
            "function": "Transport ATP-binding protein CydD",
            "id": "kb|g.960.peg.1735",
            "location": [
                [
                    "kb|g.960.c.22",
                    53155,
                    "-",
                    1767
                ]
            ],
            "md5": "348e67aaaf651fb48ac5d36b724b1472",
            "protein_families": [
                {
                    "id": "FIG01010650",
                    "release_version": "Release59",
                    "subject_db": "FIGfam",
                    "subject_description": "Transport ATP-binding protein CydD"
                }
            ],
            "protein_translation": "MNKSRQKELTRWLKQQSVISQRWLNISRLLGFVSGILIIAQAWFMARILQHMIMENIPREALLLPFTLLFLTFVLRAWVVWLRERVGYHAGQHIRFAIRRQVLDRLQQAGPAWIQGKPAGSWATLVLEQIDDMHDYYARYLPQMALAVSVPLLIVVAIFPSNWAAALILLGTAPLIPLFMALVGMGAADANRRNFLALARLSGHFLDRLRGMETLRIFGRGEAEIESIRSASEDFRQRTMEVLRLAFLSSGILEFFTSLSIALVAIYFGFSYLGELDFGHYDTGVTLAAGFLALILAPEFFQPLRDLGTFYHAKAQAVGAADSLKTFMETPLAHPQRGEAELASTDPVTIEAEDLFITSPEGKTLAGPLNFTLPAGQRAVLVGRSGSGKSSLLNALSGFLSYQGSLRINGIELRDLSPESWRKHLSWVGQNPQLPAATLRDNVLLARPDASEQELQTALDNAWVSEFLPLLPQGIDTPVGDQAARLSVGQAQRVAVARALLNPCSLLLLDEPAASLDAHSEQRVMEALNAASLRQTTLMVTHQLEDLADWDVIWVMQDGQIIEQGRYAELSVAGGPFATLLAHRQEEI",
            "protein_translation_length": 588,
            "type": "CDS"
        },
        {
            "aliases": [
                "ZP_00723503.1",
                "EcolF_01003038",
                "75239533",
                "COG0527",
                "2457342"
            ],
            "annotations": [
                [
                    "Set function to hypothetical protein",
                    "ncbi",
                    1149627647
                ]
            ],
            "co_occurring_fids": [
                [
                    "kb|g.960.peg.2008",
                    16
                ],
                [
                    "kb|g.960.peg.2207",
                    139
                ],
                [
                    "kb|g.960.peg.2343",
                    295
                ],
                [
                    "kb|g.960.peg.2496",
                    11
                ],
                [
                    "kb|g.960.peg.2555",
                    16
                ],
                [
                    "kb|g.960.peg.2608",
                    38
                ]
            ],
            "dna_sequence": "atgcgagtgttgaagttcggcggtacatcagtggcaaatgcagaacgttttctgcgggttgccgatattctggaaagcaatgccaggcaggggcaggtggccaccgtcctctctgcccccgccaaaatcaccaaccatctggtagcgatgattgaaaaaaccattagcggtcaggatgctttacccaatatcagcgatgccgaacgtatttttgccgaacttctgacgggactcgccgccgcccagccgggatttccgctggcacaattgaaaactttcgtcgaccaggaatttgcccaaataaaacatgtcctgcatggcatcagtttgttggggcagtgcccggatagcatcaacgctgcgctgatttgccgtggcgagaaaatgtcgatcgccattatggccggcgtgttagaagcgcgtggtcacaacgttaccgttatcgatccggtcgaaaaactgctggcagtgggtcattacctcgaatctaccgttgatattgctgaatccacccgccgtattgcggcaagccgcattccggctgaccacatggtgctgatggctggtttcactgccggtaatgaaaaaggcgagctggtggttctgggacgcaacggttccgactactccgctgcggtgctggcggcctgtttacgcgccgattgttgcgagatctggacggatgttgacggtgtttatacctgcgatccgcgtcaggtgcccgatgcgaggttgttgaagtcgatgtcctatcaggaagcgatggagctttcttacttcggcgctaaagttcttcacccccgcaccattacccccatcgcccagttccagatcccttgcctgattaaaaataccggaaatccccaagcaccaggtacgctcattggtgccagccgtgatgaagacgaattaccggtcaagggcatttccaatctgaataacatggcaatgttcagcgtttccggcccggggatgaaagggatggttggcatggcggcgcgcgtctttgcagcgatgtcacgcgcccgtatttccgtggtgctgattacgcaatcatcttccgaatacagtatcagtttctgcgttccgcaaagcgactgtgtgcgagctgaacgggcaatgcaggaagagttctacctggaactgaaagaaggcttactggagccgttggcggtgacggaacggctggccattatctcggtggtaggtgatggtatgcgcaccttacgtgggatctcggcgaaattctttgccgcgctggcccgcgccaatatcaacattgtcgccattgctcagggatcttctgaacgctcaatctctgtcgtggtcaataacgatgatgcgaccactggcgtgcgcgttactcatcagatgctgttcaataccgatcaggttatcgaagtgtttgtgattggcgtcggtggcgttggcggtgcgctgctggagcaactgaagcgtcagcaaagctggttgaagaataaacatatcgacttacgtgtctgcggtgttgctaactcgaaggcactgctcaccaatgtacatggccttaatctggaaaactggcaggaagaactggcgcaagccaaagagccgtttaatctcgggcgcttaattcgcctcgtgaaagaatatcatctgctgaacccggtcattgttgactgtacttccagccaggctgtggcagatcaatatgccgacttcctgcgcgaaggtttccacgttgttacgccgaacaaaaaggccaacacctcgtcgatggattactaccatcagttgcgttatgcggcggaaaaatcgcggcgtaaattcctctatgacaccaacgttggggctggattaccggttattgagaacctgcaaaatctgctcaatgctggtgatgaattgatgaagttctccggcattctttcaggttcgctttcttatatcttcggcaagttagacgaaggcatgagtttctccgaggcgaccacactggcgcgggaaatgggttataccgaaccggacccgcgagatgatctttctggtatggatgtggcgcgtaagctattgattctcgctcgtgaaacgggacgtgaactggagctggcggatattgaaattgaacctgtgctgcccgcagagtttaacgccgagggtgatgtcgccgcttttatggcgaatctgtcacagctcgacgatctctttgccgcgcgtgtggcgaaggcccgtgatgaaggaaaagttttgcgctatgttggcaatattgatgaagatggcgtctgccgcgtgaagattgccgaagtggatggtaatgatccgctgttcaaagtgaaaaatggcgaaaacgccctggccttctatagccactattatcagccgctgccgttggtactgcgcggatatggtgcgggcaatgacgttacagctgccggtgtctttgctgatctgctacgtaccctctcatggaagttaggagtctga",
            "dna_sequence_length": 2463,
            "function": "Aspartokinase (EC 2.7.2.4) / Homoserine dehydrogenase (EC 1.1.1.3)",
            "id": "kb|g.960.peg.2375",
            "location": [
                [
                    "kb|g.960.c.49",
                    11942,
                    "-",
                    2463
                ]
            ],
            "md5": "0f66dc2b3024a9739d0e912fde12b8ba",
            "protein_families": [
                {
                    "id": "FIG01290007",
                    "release_version": "Release59",
                    "subject_db": "FIGfam",
                    "subject_description": "Aspartokinase (EC 2.7.2.4) / Homoserine dehydrogenase (EC 1.1.1.3)"
                }
            ],
            "protein_translation": "MRVLKFGGTSVANAERFLRVADILESNARQGQVATVLSAPAKITNHLVAMIEKTISGQDALPNISDAERIFAELLTGLAAAQPGFPLAQLKTFVDQEFAQIKHVLHGISLLGQCPDSINAALICRGEKMSIAIMAGVLEARGHNVTVIDPVEKLLAVGHYLESTVDIAESTRRIAASRIPADHMVLMAGFTAGNEKGELVVLGRNGSDYSAAVLAACLRADCCEIWTDVDGVYTCDPRQVPDARLLKSMSYQEAMELSYFGAKVLHPRTITPIAQFQIPCLIKNTGNPQAPGTLIGASRDEDELPVKGISNLNNMAMFSVSGPGMKGMVGMAARVFAAMSRARISVVLITQSSSEYSISFCVPQSDCVRAERAMQEEFYLELKEGLLEPLAVTERLAIISVVGDGMRTLRGISAKFFAALARANINIVAIAQGSSERSISVVVNNDDATTGVRVTHQMLFNTDQVIEVFVIGVGGVGGALLEQLKRQQSWLKNKHIDLRVCGVANSKALLTNVHGLNLENWQEELAQAKEPFNLGRLIRLVKEYHLLNPVIVDCTSSQAVADQYADFLREGFHVVTPNKKANTSSMDYYHQLRYAAEKSRRKFLYDTNVGAGLPVIENLQNLLNAGDELMKFSGILSGSLSYIFGKLDEGMSFSEATTLAREMGYTEPDPRDDLSGMDVARKLLILARETGRELELADIEIEPVLPAEFNAEGDVAAFMANLSQLDDLFAARVAKARDEGKVLRYVGNIDEDGVCRVKIAEVDGNDPLFKVKNGENALAFYSHYYQPLPLVLRGYGAGNDVTAAGVFADLLRTLSWKLGV",
            "protein_translation_length": 820,
            "subsystem_data": [
                [
                    "Lysine Biosynthesis DAP Pathway",
                    "A",
                    "Aspartokinase (EC 2.7.2.4)"
                ],
                [
                    "Threonine and Homoserine Biosynthesis",
                    "1.x",
                    "Aspartokinase (EC 2.7.2.4)"
                ],
                [
                    "Threonine and Homoserine Biosynthesis",
                    "1.x",
                    "Homoserine dehydrogenase (EC 1.1.1.3)"
                ]
            ],
            "subsystems": [
                "Lysine Biosynthesis DAP Pathway",
                "Methionine Biosynthesis",
                "Threonine and Homoserine Biosynthesis"
            ],
            "type": "CDS"
        },
        {
            "aliases": [
                "ZP_00724505.1",
                "EcolF_01002306",
                "75240588",
                "COG2920",
                "2456622"
            ],
            "annotations": [
                [
                    "Set function to COG3101: Uncharacterized protein conserved in bacteria",
                    "ncbi",
                    1149627647
                ],
                [
                    "Set function to tRNA 2-thiouridine synthesizing protein E (EC 2.8.1.-)",
                    "gjo",
                    1197143618
                ]
            ],
            "co_occurring_fids": [
                [
                    "kb|g.960.peg.1985",
                    19
                ]
            ],
            "dna_sequence": "atgctgatcttcgaaggtaaagagatagaaacggataccgaaggctatctcaaagaaagcagccagtggagtgagccactggcggtggtgattgcagagaacgaagggattgcgctgtcgccagaacactgggaagtggtgcgttttgtgcgtgatttctatctggaattcaatacttctccggcgattcgtatgctggtaaaagcgatggcgaataaatttggcgaagagaaaggcaatagccgctatctgtaccgactgttcccgaaaggtccggcaaagcaagccaccaaaattgctggcctgcctaaaccggtaaaatgcatttaa",
            "dna_sequence_length": 330,
            "function": "tRNA 2-thiouridine synthesizing protein E (EC 2.8.1.-)",
            "id": "kb|g.960.peg.1028",
            "location": [
                [
                    "kb|g.960.c.65",
                    5575,
                    "-",
                    330
                ]
            ],
            "md5": "2748c3ad89a8a5e27fc4dabd6075d5c4",
            "protein_families": [
                {
                    "id": "FIG00141658",
                    "release_version": "Release59",
                    "subject_db": "FIGfam",
                    "subject_description": "Putative sulfite reductase, gamma subunit (EC 1.8.99.3)"
                }
            ],
            "protein_translation": "MLIFEGKEIETDTEGYLKESSQWSEPLAVVIAENEGIALSPEHWEVVRFVRDFYLEFNTSPAIRMLVKAMANKFGEEKGNSRYLYRLFPKGPAKQATKIAGLPKPVKCI",
            "protein_translation_length": 109,
            "type": "CDS"
        }
    ],
    "gc_content": 50.4968209527885,
    "genetic_code": 11,
    "id": "kb|g.960",
    "md5": "2618042895ad48071fde3fa8e5728928",
    "num_contigs": 88,
    "scientific_name": "Escherichia coli F11 partial",
    "source": "KBase Central Store",
    "source_id": "340197.3",
    "taxonomy": "Bacteria; Proteobacteria; Gammaproteobacteria; Enterobacteriales; Enterobacteriaceae; Escherichia; Escherichia coli F11"
}
'''
        return json.loads(obj_json)