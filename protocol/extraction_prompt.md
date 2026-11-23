You are extracting data from ONE included study for a systematic review that supports the UnLost
project (papyri that are read, Greek letters that are identified, the Herculaneum papyri, and
virtual unwrapping).

Read the full text below and fill every field from what the paper actually reports. Never guess:
use null (or an empty list) when the paper does not state it. Use only the allowed values for
coded fields; put anything else under "other" and explain in "notes".

Fields:
- object_class: one of "carbonized_rolled_scroll", "opened_or_fragmentary_papyrus",
  "other_historical_document", "synthetic_or_phantom", "other".
- object_name: the object as named (e.g. "PHerc. Paris. 4", "En-Gedi scroll", "Villa dei Papiri fragments"), or null.
- primary_task: one of "unwrapping_or_flattening", "ink_detection_or_hidden_text_imaging",
  "character_or_text_recognition", "writer_or_script_analysis", "text_restoration_or_fragment_assembly",
  "herculaneum_papyrology_or_chemistry", "acquisition_or_imaging", "other".
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
  "character_detections", "glyph_or_hand_classification", "spectral_or_chemical_maps", "dataset_or_benchmark",
  "restored_text_or_joins", "edition_or_interpretation", "other".
- corpus_origin: list from "herculaneum", "other_papyri", "en_gedi_or_sealed_documents", "other_historical_document", "modern_or_synthetic".
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
