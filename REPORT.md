# Technical Report — [The Reason for HealtBridge and Why I Choose to go to the Health Sector in Machine Learning]

**Team ID:** Vicarioy  
**Domain:** Healthcare  
**Model:** qwen2.5-1.5b-instruct-q4_k_m.gguf

---

## Problem

Nigeria has over 200 million people and has approximately 85,000 to 90,000 registered medical practitioners according to Medical and Dental Council of Nigeria(MDCN) but due to the Japa issue and the renewal of license, the only actively practicing medical practitioners are not up to 60,000; roughly 1 doctor per 4,000 citizens. In rural and peri-urban communities, university students going to local pharmacy to seek help instead of going to medical centres, patients often have no access to basic health information before deciding whether to seek care. 
Incorrect triage decisions, waiting too long, going to the wrong pratitioners like local pharmacy that aren't registered, seeking advices from the wrong people or travelling unnecessarily; cost lives and money. Internet connectivity is unreliable or unaffordable across large parts of Nigeria and sub-Saharan Africa, making cloud-based health AI tools inaccessible to those who need them most.

HealthBridge is an offline patient education and triage-support LLM assistant that runs entirely on a standard laptop with no internet connection, no GPU, and no recurring cloud cost. It explains symptoms, describes treatments (e.g. oral rehydration therapy for cholera and diarrheal disease), guides users on when to seek urgent hospital care, and stop people from asking the wrong people for advice or prescription without claiming to replace professional diagnosis.

Target user: community health workers, patients, students, and caregivers in Nigerian and broader African communities with limited connectivity and limited access to medical professionals.
---

## Design Decisions

- **Base model:** 
    Qwen2.5-1.5B-Instruct was selected for its strong instruction-following capability at a small parameter count from 7B to 72B models but the 1.5 B Model was choose because of the project and it is good for multilingual processing. At 1.5B parameters it fits comfortably within an 8GB RAM budget while producing coherent, medically contextual responses to patient education prompts.
- **Quantization:** 
    GGUF Q4_K_M was chosen as the optimal balance between model quality and memory footprint. Q4_K_M applies 4-bit quantization with K-means grouping on key weight matrices, preserving more accuracy than flat Q4_0 while using less RAM than Q5 or Q8 variants, because it is good for general summaries and it is lightweighted for standard desktop and can run on mobile devices also.
- **Alternatives considered:** 
    - Phi-3-mini-4k-instruct (3.8B): stronger reasoning but higher RAM usage risked exceeding 8GB budget on evaluation hardware.
    - Qwen2.5-0.5B: fits easily in RAM but output quality insufficient for reliable patient education responses.
    - Llama-3.2-1B: comparable size but Qwen2.5 showed better instruction-following on health Q&A prompts in local testing.

- **Runtime:** 
    llama.cpp: only supported runtime per competition rules, and the industry standard for CPU-only GGUF inference on x86-64 hardware.

- **Domain framing:** 
    Healthcare & Medical: specifically patient education and triage support, not clinical diagnosis. The model is explicitly scoped as a complement to professional care, to guide people when they have to see medical pratitioners and not there family, friends or neighbours for advice and it is not a replacement to medical pratitioners.

---

## Constraints

- Target: 8 GB RAM, integrated GPU, Ubuntu 22.04
- No GPU acceleration — pure CPU inference via llama.cpp
- Any specific connectivity or data availability constraints relevant to your domain

- My Hardware: Intel Core i5-8265U (4c/8t, 1.6GHz base), 16GB RAM, Intel UHD 620 integrated GPU,  Windows 11
- No discrete GPU — CPU-only inference throughout
- Evaluation target: ADTC Standard Laptop (i5 10th-12th gen, 8GB DDR4, integrated GPU, Ubuntu 22.04)
- Zero network dependencies during inference — model downloaded via download_model.sh, all subsequent runs fully offline
- Model file not committed to git — downloaded fresh by evaluator via public Hugging Face URL

---

## Benchmarks

| Metric | Value |
|---|---|
| Machine | Dell Latitude 5400 |
| RAM at peak | 1.7 GB |
| First token latency | 9051.95 ms |
| Generation speed | 16.76 t/s |
| Thermal throttling | None observed |
| CPU utilization (p99) | 74.3%  |
|  OS | Windows 11 (10.0.22621) |

**Projected competition scores:**
- Sperf: 100/100 (16.76 t/s exceeds TPS_REFERENCE of 15.0)
- Seff: ~75.7/100 (peak RAM 1.7GB vs 7GB budget)
- Pthermal: 0 (no throttling observed)

Model architecture confirmed as qwen2 with 32768 context length. 
params_match: true per profiler schema validation.

These are self-reported development benchmarks. Official scores are measured by the ADTC profiler on the standard evaluation machine.
