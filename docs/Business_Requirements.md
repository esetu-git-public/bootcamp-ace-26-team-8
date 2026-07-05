# Business Requirements

## Functional Requirements

1. The system shall accept borrower information as input.
2. The system shall preprocess the input data before prediction.
3. The system shall predict whether the borrower is likely to default.
4. The system shall classify the prediction as:

   * Default
   * No Default
5. The system shall display the prediction result to the user.

## Non-Functional Requirements

* The system should provide accurate predictions.
* The system should produce results quickly.
* The solution should be scalable for larger datasets.
* The system should be reliable and easy to maintain.
* The model should be easy to update with new training data.

## Business Benefits

* Minimize financial losses from loan defaults.
* Improve the efficiency of the loan approval process.
* Support better risk management.
* Enable data-driven lending decisions.
* Improve overall operational efficiency.

## Assumptions

* Historical loan data is accurate and complete.
* The selected dataset represents real-world lending scenarios.
* The trained model will generalize well to new borrower data.

## Constraints

* Prediction accuracy depends on the quality of the dataset.
* Limited features may reduce model performance.
* The model requires periodic retraining using updated loan records.
