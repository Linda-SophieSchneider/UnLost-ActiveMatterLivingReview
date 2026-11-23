You are extracting data from ONE included study for a systematic review that supports the UnLost
project (non-invasive recovery, reading and study of carbonised and damaged ancient manuscripts,
above all the Herculaneum papyri).

Read the full text below and fill every field from what the paper actually reports. Never guess:
use null (or an empty list) when the paper does not state it. Use only the allowed values for
coded fields; put anything else under "other" and explain in "notes".

Fields:
- object_class: one of "carbonized_rolled_scroll", "opened_or_fragmentary_papyrus",
  "other_ancient_manuscript", "synthetic_or_phantom", "other".
- object_name: the object as named (e.g. "PHerc. Paris. 4", "En-Gedi scroll", "Villa dei Papiri fragments"), or null.
- primary_task: one of "acquisition_or_imaging", "virtual_unwrapping_or_segmentation", "ink_detection_or_enhancement",
  "text_recognition_or_decipherment", "script_or_writer_analysis", "chemical_or_material_characterisation",
  "registration_provenance_or_metadata", "papyrological_study_or_context", "other".
- method_family: one of "classical_signal_processing", "machine_learning_cnn", "transformer_or_foundation_model",
  "generative_or_self_supervised", "manual_or_expert_workflow", "physical_or_chemical_analysis", "other".
- imaging_modality: list from "micro_ct", "synchrotron_or_phase_contrast_ct", "multispectral_or_hyperspectral",
  "xrf", "ftir_raman_xrd", "photoacoustic", "visible_light_or_infrared", "neural_rendering", "none", "other".
- instrument: scanner, beamline or device with its setting, at most 20 words.
- resolution_um: voxel or pixel size in micrometres (number), or null.
- n_objects: number of physical objects (scrolls, fragments, samples) studied (integer), or null.
- n_scans: number of scans, images or measurements analysed (integer), or null.
- n_annotated_samples: number of annotated or ground-truth samples used for training or evaluation (integer), or null.
- outputs: list from "segmented_surfaces", "flattened_images", "ink_masks", "transcribed_text",
  "glyph_or_hand_classification", "spectral_or_chemical_maps", "dataset_or_benchmark",
  "metadata_or_provenance_framework", "edition_or_interpretation", "other".
- corpus_origin: list from "herculaneum", "dead_sea_or_en_gedi", "egyptian_papyri", "other_ancient", "modern_or_synthetic".
- metrics: list of the quantitative measures reported (e.g. "IoU", "character error rate"), at most 8 items.
- validation: one of "quantitative_vs_ground_truth", "expert_assessment", "visual_only", "none".
- code_available, data_available: true, false, or null (true only if a repository or archive is named).
- rob: risk-of-bias ratings, each "low", "some_concerns", or "high", with a justification of at most
  20 words: D1_ground_truth, D2_sample_representativeness, D3_acquisition_documentation,
  D4_evaluation_validity, D5_data_code_availability, D6_expert_validation.
- notes: at most 40 words.

Respond with ONLY one JSON object with exactly these keys:
{"object_class": ..., "object_name": ..., "primary_task": ..., "method_family": ..., "imaging_modality": [...],
 "instrument": ..., "resolution_um": ..., "n_objects": ..., "n_scans": ..., "n_annotated_samples": ...,
 "outputs": [...], "corpus_origin": [...], "metrics": [...], "validation": ..., "code_available": ..., "data_available": ...,
 "rob": {"D1_ground_truth": {"rating": ..., "why": ...}, "D2_sample_representativeness": {...},
         "D3_acquisition_documentation": {...}, "D4_evaluation_validity": {...},
         "D5_data_code_availability": {...}, "D6_expert_validation": {...}},
 "notes": ...}
<!-- RECORD TEMPLATE -->
Title: {title}
Year: {year}
Venue: {venue}

Full text:
{body}
