/*
A KBase module: ElectronicAnnotationMethods
This module contains the following methods:

  InterPro2GO
  EC2GO
  UniProtKB-Keyword2GO

*/

module ElectronicAnnotationMethods {

    typedef string ws_name;

    /*
        The workspace ID for a Genome data object.
        @id ws KBaseGenomes.Genome
    */
    typedef string ws_genome_id;

    /*
        The workspace ID for a OntologyTranslation data object.
        @id ws KBaseOntology.OntologyTranslation
    */
    typedef string ws_translation_id;

    /*
        workspace_name - the name of the workspace for input/output
        genome_ref - reference to the input genome object
        ontology_translation_ref - optional reference to user specified ontology translation map

        @optional ontology_translation_ref
    */
    typedef structure {
        ws_name workspace_name;
        ws_genome_id genome_ref;
        ws_ontology_translation_id ontology_translation_ref;
    } ElectronicAnnotationParams;

    typedef structure {
        string report_name;
        string report_ref;
        ws_genome_id new_genome_ref;
        int n_total_features;
        int n_features_mapped;
    } ElectronicAnnotationResults;


    funcdef interpro2go(ElectronicAnnotationParams params) returns (ElectronicAnnotationResults output)
        authentication required;

    funcdef ec2go(ElectronicAnnotationParams params) returns (ElectronicAnnotationResults output)
        authentication required;

    funcdef uniprotkb_keyword2go(ElectronicAnnotationParams params) returns (ElectronicAnnotationResults output)
        authentication required;

};
