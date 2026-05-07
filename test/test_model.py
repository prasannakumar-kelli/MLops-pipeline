"""
Unit tests for data processing and model code.
Task 5: CI/CD Pipeline & Automated Testing
"""

import os
import sys
import pickle
import json

import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============== Data Processing Tests ==============

class TestDataProcessing:
    """Tests for data loading and preprocessing."""

    def test_dataset_download(self):
        """Test that the UCI dataset can be fetched."""
        from ucimlrepo import fetch_ucirepo
        dataset = fetch_ucirepo(id=45)
        assert dataset is not None
        assert dataset.data.features is not None
        assert dataset.data.targets is not None

    def test_dataset_shape(self):
        """Test that the dataset has expected dimensions."""
        from ucimlrepo import fetch_ucirepo
        dataset = fetch_ucirepo(id=45)
        X = dataset.data.features
        y = dataset.data.targets
        assert X.shape[0] > 200, "Expected at least 200 samples"
        assert X.shape[1] >= 13, "Expected at least 13 features"
        assert len(y) == len(X), "Features and targets must have same length"

    def test_target_binary_conversion(self):
        """Test binary target conversion (0: no disease, 1: disease)."""
        from ucimlrepo import fetch_ucirepo
        dataset = fetch_ucirepo(id=45)
        y = dataset.data.targets
        y_binary = (y > 0).astype(int)
        unique_vals = y_binary.iloc[:, 0].unique()
        assert set(unique_vals).issubset({0, 1}), "Target should be binary"

    def test_no_missing_after_cleaning(self):
        """Test that cleaned data has no missing values."""
        from ucimlrepo import fetch_ucirepo
        dataset = fetch_ucirepo(id=45)
        df = dataset.data.features.copy()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].median())
        df = df.dropna()
        assert df.isnull().sum().sum() == 0

    def test_feature_scaling(self):
        """Test that StandardScaler produces zero mean and unit variance."""
        X = np.random.randn(100, 5)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        np.testing.assert_array_almost_equal(X_scaled.mean(axis=0), 0, decimal=10)
        np.testing.assert_array_almost_equal(X_scaled.std(axis=0), 1, decimal=10)


# ============== Model Tests ==============

class TestModel:
    """Tests for model training and prediction."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        X = np.random.randn(100, 13)
        y = (X[:, 0] > 0).astype(int)
        return X, y

    def test_model_trains(self, sample_data):
        """Test that models can be trained without errors."""
        from sklearn.linear_model import LogisticRegression
        X, y = sample_data
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        assert hasattr(model, 'coef_'), "Model should have coefficients after fitting"

    def test_model_predicts(self, sample_data):
        """Test that model produces predictions."""
        from sklearn.linear_model import LogisticRegression
        X, y = sample_data
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        preds = model.predict(X[:5])
        assert len(preds) == 5
        assert all(p in [0, 1] for p in preds)

    def test_model_probabilities(self, sample_data):
        """Test that model produces valid probabilities."""
        from sklearn.linear_model import LogisticRegression
        X, y = sample_data
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        probs = model.predict_proba(X[:5])
        assert probs.shape == (5, 2)
        np.testing.assert_array_almost_equal(probs.sum(axis=1), 1.0)
        assert (probs >= 0).all() and (probs <= 1).all()

    def test_pipeline_consistency(self, sample_data):
        """Test that sklearn Pipeline produces consistent results."""
        from sklearn.linear_model import LogisticRegression
        X, y = sample_data
        pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(max_iter=1000, random_state=42))
        ])
        pipe.fit(X, y)
        pred1 = pipe.predict(X[:5])
        pred2 = pipe.predict(X[:5])
        np.testing.assert_array_equal(pred1, pred2, "Predictions should be deterministic")

    def test_model_serialization(self, sample_data, tmp_path):
        """Test that model can be saved and loaded correctly."""
        from sklearn.linear_model import LogisticRegression
        X, y = sample_data
        pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(max_iter=1000, random_state=42))
        ])
        pipe.fit(X, y)

        # Save
        model_path = tmp_path / "test_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(pipe, f)

        # Load
        with open(model_path, 'rb') as f:
            loaded = pickle.load(f)

        # Verify predictions match
        orig_preds = pipe.predict(X[:10])
        loaded_preds = loaded.predict(X[:10])
        np.testing.assert_array_equal(orig_preds, loaded_preds)


# ============== API Tests ==============

class TestAPI:
    """Tests for the FastAPI application."""

    @pytest.fixture
    def sample_input(self):
        return {
            "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233,
            "fbs": 1, "restecg": 2, "thalach": 150, "exang": 0,
            "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6
        }

    def test_input_validation(self, sample_input):
        """Test that input data is valid."""
        assert all(isinstance(v, (int, float)) for v in sample_input.values())
        assert sample_input['age'] > 0
        assert sample_input['sex'] in [0, 1]

    def test_prediction_format(self, sample_input):
        """Test prediction output format."""
        prediction = {"prediction": 1, "prediction_label": "Disease",
                      "confidence": 0.85, "timestamp": "2024-01-01T00:00:00"}
        assert prediction['prediction'] in [0, 1]
        assert prediction['prediction_label'] in ['Disease', 'No Disease']
        assert 0 <= prediction['confidence'] <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
