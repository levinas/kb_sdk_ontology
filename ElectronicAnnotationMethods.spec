/*
A KBase module: ElectronicAnnotationMethods
This module wraps the following methods:

  interpro2go          -> InterPro2GO
  ec2go                -> EC2GO
  uniprotkb_keyword2go -> UniProtKB-Keyword2GO

*/

module ElectronicAnnotationMethods {

    /*
        workspace - the name of the workspace for input/output
        input_genome - reference to the input genome object
        ontology_translation - optional reference to user specified ontology translation map
        output_genome - the name of the mapped genome annotation object

        @optional ontology_translation
    */
    typedef structure {
        string workspace;
        string input_genome;
        string ontology_translation;
        string output_genome;
    } ElectronicAnnotationParams;

    typedef structure {
        string report_name;
        string report_ref;
        string output_genome_ref;
        int n_total_features;
        int n_features_mapped;
    } ElectronicAnnotationResults;


    funcdef remap_annotations_with_interpro2go(ElectronicAnnotationParams params) returns (ElectronicAnnotationResults output)
        authentication required;

    funcdef remap_annotations_with_ec2go(ElectronicAnnotationParams params) returns (ElectronicAnnotationResults output)
        authentication required;

    funcdef remap_annotations_with_uniprotkb_keyword2go(ElectronicAnnotationParams params) returns (ElectronicAnnotationResults output)
        authentication required;

};
