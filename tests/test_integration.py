"""
Integration tests for complete workflow.

Tests cover:
- End-to-end calculation workflow
- Full pipeline regression (golden test)
- File I/O operations
- Report generation
"""

import pytest
import tempfile
import json
import numpy as np
from pathlib import Path
from data_processor import calculate_metrics, save_results


def test_full_pipeline_golden(sample_input_data):
    """
    Full pipeline regression: same input must yield expected structure and types.
    Run before/after refactors to ensure no behaviour change. (Upgrade plan Phase 1.1, 4.2)
    """
    resultados, densidades_instrumento, pitches = calculate_metrics(sample_input_data)
    # Required top-level keys (English)
    assert "density" in resultados
    assert "spectral_moments" in resultados
    assert "additional_metrics" in resultados
    assert "texture" in resultados
    assert "timbre" in resultados
    assert "orchestration" in resultados
    d = resultados["density"]
    assert "interval" in d and "instrument" in d and "total" in d
    assert isinstance(d["interval"], (int, float))
    assert isinstance(d["instrument"], (int, float))
    assert isinstance(d["total"], (int, float))
    assert len(pitches) >= len(sample_input_data["notes"])
    assert len(densidades_instrumento) == len(sample_input_data["notes"])
    assert all(0 <= p <= 127 for p in pitches)
    assert d["interval"] > 0 and d["instrument"] > 0
    assert d["total"] > 0 and np.isfinite(d["total"])
    assert d["weighted"] >= 0 and d["refined"] >= 0


class TestCompleteWorkflow:
    """Test complete calculation workflow."""
    
    def test_complete_calculation_workflow(self, sample_input_data):
        """Test complete workflow from input to results."""
        # Step 1: Calculate metrics
        resultados, densidades, pitches = calculate_metrics(sample_input_data)
        
        # Step 2: Verify results structure
        assert 'density' in resultados
        assert 'spectral_moments' in resultados
        assert 'additional_metrics' in resultados
        
        # Step 3: Verify density values
        densidade = resultados['density']
        assert 'interval' in densidade
        assert 'instrument' in densidade
        assert 'total' in densidade
        
        # Step 4: Verify all values are numeric
        assert isinstance(densidade['interval'], (int, float))
        assert isinstance(densidade['instrument'], (int, float))
        assert isinstance(densidade['total'], (int, float))
    
    def test_workflow_with_different_weight_factors(self, sample_input_data):
        """Test workflow with different weight factors."""
        results = []
        
        for weight in [0.0, 0.5, 1.0]:
            sample_input_data['weight_factor'] = weight
            resultados, _, _ = calculate_metrics(sample_input_data)
            results.append(resultados['density']['weighted'])
        
        # Results should differ for different weights
        assert len(set(results)) > 1, "Different weights should produce different results"


class TestFileOperations:
    """Test file I/O operations."""
    
    def test_save_results(self, sample_input_data):
        """Test saving results to file."""
        resultados, _, _ = calculate_metrics(sample_input_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            saved_path = save_results(resultados, temp_path)
            
            assert saved_path == temp_path
            assert Path(temp_path).exists()
            
            # Verify file content
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            
            assert 'density' in loaded
        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)
    
    def test_save_results_invalid_path(self, sample_input_data):
        """Test saving to invalid path (graceful: raises OSError or returns None)."""
        resultados, _, _ = calculate_metrics(sample_input_data)
        try:
            out = save_results(resultados, "/invalid/path/that/does/not/exist.json")
            assert out is None
        except (OSError, IOError):
            pass


class TestDataConsistency:
    """Test data consistency across calculations."""
    
    def test_results_consistency(self, sample_input_data):
        """Test that repeated calculations produce consistent results."""
        resultados1, _, _ = calculate_metrics(sample_input_data)
        resultados2, _, _ = calculate_metrics(sample_input_data)
        # Results should be consistent (small float noise allowed across runs)
        d1, d2 = resultados1["density"], resultados2["density"]
        assert float(d1["interval"]) == pytest.approx(float(d2["interval"]), rel=1e-6)
        assert float(d1["instrument"]) == pytest.approx(float(d2["instrument"]), rel=1e-6)
    
    def test_pitch_conversion_consistency(self, sample_input_data):
        """Test that pitch conversions are consistent."""
        resultados, _, pitches = calculate_metrics(sample_input_data)
        assert len(pitches) == len(sample_input_data["notes"])
        assert all(0 <= p <= 127 for p in pitches)


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""

    def test_removed_combination_tones_rejected(self, sample_input_data):
        from error_handler import InputError

        sample_input_data["calculate_combination_tones"] = True
        with pytest.raises(InputError, match="calculate_combination_tones"):
            calculate_metrics(sample_input_data)

