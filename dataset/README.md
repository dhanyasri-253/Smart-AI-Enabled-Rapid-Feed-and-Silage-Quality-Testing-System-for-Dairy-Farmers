# Dataset Protocol & Specifications — SmartSilageAI (SIH26111)

## Current Status
- **Dataset Status**: `Pending Field Collection & Laboratory Validation`
- **Validation Authority**: Recommended ICAR-NDRI / College of Veterinary Science & Animal Husbandry
- **Integrity Rule**: *NO fabricated or synthetic random numbers are used as training data.*

## Required Dataset Schema for ML Training

To train a scientifically valid quality prediction model, samples must undergo laboratory proximate wet-chemistry analysis or calibrated NIRS alongside field measurements:

| Feature Name | Type | Measurement Method | Standard Range (Corn Silage) | Source / Instrument |
|--------------|------|--------------------|------------------------------|---------------------|
| `ph` | Continuous | Direct electrode / pH test strip | 3.7 - 4.2 | Portable digital pH meter |
| `moisture_pct` | Continuous | Koster tester / Hot air oven | 60.0% - 70.0% | Laboratory / Field moisture tester |
| `temperature_c` | Continuous | Probe thermometer | Ambient to 30.0°C | Stainless digital compost probe |
| `crude_protein_pct` | Continuous | Kjeldahl method (N x 6.25) | 7.5% - 9.5% | Laboratory proximate analysis |
| `ndf_pct` | Continuous | Neutral Detergent Fiber | 38.0% - 48.0% | Van Soest fiber analyzer |
| `adf_pct` | Continuous | Acid Detergent Fiber | 24.0% - 30.0% | Van Soest fiber analyzer |
| `ash_pct` | Continuous | Muffle furnace combustion | 3.5% - 6.0% | Gravimetric analysis |
| `flieg_score` | Derived | Fermentation quality index | 0 - 100 | Calculated from pH & dry matter |
| `quality_label` | Categorical | Target class | Good / Needs Attention / Poor | Expert panel / Lab validation |

## Data Collection Protocol for SIH Expansion

1. **Phase 1: Regional Field Sampling**:
   Partner with district dairy unions (e.g. Amul/NDDB milk societies) across agro-climatic zones in India.
2. **Phase 2: Split-Sample Testing**:
   For every batch, one portion is field-tested by extension workers (pH, moisture, temperature, visual log), and a duplicate split is sent for certified proximate analysis.
3. **Phase 3: Image Dataset Annotation**:
   Standardized photography (constant distance, 18% gray card, natural lighting) to curate visual indicators (mycotoxin mold stains, clostridial dark slime, aerobic heating signs) for future computer vision transfer learning.
