# Experiment log

Prespecified candidates: logistic regression C=0.1 and C=1.0; fixed seed; train-fit median imputer and scaler in each pipeline. No iterative test-driven optimization.

- logistic_C=0.1: validation ROC-AUC=0.7632.
- logistic_C=1.0: validation ROC-AUC=0.7642.

Selected logistic_C=1.0 using validation ROC-AUC (ties: first candidate). Threshold=0.25 selected by validation F1 from 0.20 to 0.80 in 0.05 increments (ties: lower threshold). Model JSON was written before final-test scoring.
