/*
A KBase module: ElectronicAnnotationMethods
This module wraps the following methods:

  interpro2go          -> InterPro2GO
  ec2go                -> EC2GO
  uniprotkb_keyword2go -> UniProtKB-Keyword2GO

*/

module ElectronicAnnotationMethods {

    /*
        workspace_name - the name of the workspace for input/output
        input_genome_ref - reference to the input genome object
        ontology_translation_ref - optional reference to user specified ontology translation map
        output_genome_name - the name of the mapped genome annotation object

        @optional ontology_translation_ref
    */
    typedef structure {
        string workspace_name;
        string input_genome_ref;
        string ontology_translation_ref;
        string output_genome_name;
    } ElectronicAnnotationParams;

    typedef structure {
        string report_name;
        string report_ref;
        string output_genome_ref;
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
