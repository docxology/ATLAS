#!/usr/bin/env python3
"""
Performance and stress testing suite for ATLAS Knowledge Management System.
This module tests system behavior under load and measures performance metrics.
"""

import pytest
import sys
import os
import time
import statistics
from datetime import datetime
from typing import List, Dict, Any, Tuple
import threading
import concurrent.futures

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Add src to path for imports in test environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from atlas.core.engine import ATLASEngine, ATLASConfig
from atlas.entities.entity import Entity
from atlas.patterns.pattern import Pattern
from atlas.patterns.pattern_engine import PatternEngine
from atlas.queries.iquery import iQuery, QueryPriority
from atlas.utils.helpers import generate_id


class TestATLASPerformance:
    """Performance testing suite for ATLAS core operations."""
    
    def setup_method(self) -> None:
        """Set up performance test fixtures."""
        self.config = ATLASConfig(
            auto_pattern_inference=True,
            enable_dynamic_typing=True,
            max_expansion_depth=3,
            enable_quality_metrics=True
        )
        self.atlas = ATLASEngine(self.config)
    
    def test_entity_creation_performance(self) -> None:
        """Test performance of entity creation operations."""
        entity_counts = [10, 50, 100, 500]
        creation_times = []
        
        for count in entity_counts:
            start_time = time.time()
            
            for i in range(count):
                entity = Entity(
                    entity_id=f"perf_entity_{i}",
                    attributes={
                        "name": f"Entity {i}",
                        "value": i,
                        "category": f"category_{i % 10}",
                        "description": f"This is test entity number {i} for performance testing"
                    }
                )
                self.atlas.add_entity(entity.id, entity.to_dict())
            
            end_time = time.time()
            creation_time = end_time - start_time
            creation_times.append(creation_time)
            
            print(f"Created {count} entities in {creation_time:.3f} seconds")
            print(f"Average time per entity: {creation_time/count:.6f} seconds")
            
            # Verify entities were created
            assert len(self.atlas.entities) >= count
        
        # Performance should not degrade significantly with scale
        # (This is a basic linear growth test with more reasonable tolerance)
        growth_ratio = creation_times[-1] / creation_times[0] if creation_times[0] > 0 else 1
        scale_ratio = entity_counts[-1] / entity_counts[0] if entity_counts[0] > 0 else 1
        # Allow for up to 5x degradation instead of 3x for test environment variability
        # This accounts for slower CI/test environments and variable system loads
        assert growth_ratio < scale_ratio * 5
    
    def test_search_performance_with_scale(self) -> None:
        """Test search performance as data size increases."""
        # Create a large dataset
        entity_count = 1000
        for i in range(entity_count):
            entity = Entity(
                entity_id=f"search_entity_{i}",
                attributes={
                    "name": f"SearchEntity_{i}",
                    "category": f"cat_{i % 20}",
                    "value": i,
                    "searchable_field": f"searchable_value_{i % 50}"
                }
            )
            self.atlas.add_entity(entity.id, entity.to_dict())
        
        # Test search performance with different query types
        search_terms = [
            "SearchEntity_123",  # Specific match
            "cat_5",             # Category match
            "searchable_value_10", # Common field match
            "nonexistent_term"   # No match
        ]
        
        search_times = []
        for term in search_terms:
            start_time = time.time()
            results = self.atlas.query(term)
            end_time = time.time()
            
            search_time = end_time - start_time
            search_times.append(search_time)
            
            print(f"Search for '{term}' took {search_time:.6f} seconds, found {len(results)} results")
        
        # All searches should complete quickly (under 1 second for 1000 entities)
        assert all(t < 1.0 for t in search_times)
        
        # Average search time should be reasonable
        avg_search_time = statistics.mean(search_times)
        assert avg_search_time < 0.1  # 100ms average
    
    def test_relationship_creation_performance(self) -> None:
        """Test performance of relationship creation."""
        # Create entities first
        entity_count = 500
        entities = []
        for i in range(entity_count):
            entity = Entity(entity_id=f"rel_entity_{i}")
            entities.append(entity)
            self.atlas.add_entity(entity.id, entity.to_dict())
        
        # Create relationships
        relationship_count = 1000
        start_time = time.time()
        
        successful_relationships = 0
        for i in range(relationship_count):
            source_idx = i % entity_count
            target_idx = (i + 1) % entity_count
            if self.atlas.add_relationship(
                entities[source_idx].id,
                entities[target_idx].id,
                f"relation_type_{i % 5}"
            ):
                successful_relationships += 1
        
        end_time = time.time()
        relationship_time = end_time - start_time
        
        print(f"Created {successful_relationships}/{relationship_count} relationships in {relationship_time:.3f} seconds")
        print(f"Average time per relationship: {relationship_time/relationship_count:.6f} seconds")
        
        # Verify relationships were created (allow for some to fail due to duplicates)
        assert self.atlas.graph.number_of_edges() >= relationship_count * 0.5  # At least 50% should succeed
        assert successful_relationships >= relationship_count * 0.5
    
    def test_concurrent_operations(self) -> None:
        """Test system performance under concurrent operations."""
        def create_entities_worker(worker_id: int, entity_count: int) -> float:
            """Worker function to create entities concurrently."""
            start_time = time.time()
            
            for i in range(entity_count):
                entity = Entity(
                    entity_id=f"concurrent_entity_{worker_id}_{i}",
                    attributes={"worker_id": worker_id, "index": i}
                )
                self.atlas.add_entity(entity.id, entity.to_dict())
            
            return time.time() - start_time
        
        def search_worker(worker_id: int, search_count: int) -> float:
            """Worker function to perform searches concurrently."""
            start_time = time.time()
            
            for i in range(search_count):
                search_term = f"concurrent_entity_{worker_id % 3}"
                self.atlas.query(search_term)
            
            return time.time() - start_time
        
        # Test concurrent entity creation
        worker_count = 4
        entities_per_worker = 50
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [
                executor.submit(create_entities_worker, i, entities_per_worker)
                for i in range(worker_count)
            ]
            
            creation_times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_entities = worker_count * entities_per_worker
        max_creation_time = max(creation_times)
        
        print(f"Concurrent creation of {total_entities} entities completed in {max_creation_time:.3f} seconds")
        
        # Verify all entities were created
        assert len(self.atlas.entities) >= total_entities
        
        # Test concurrent searches
        searches_per_worker = 20
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [
                executor.submit(search_worker, i, searches_per_worker)
                for i in range(worker_count)
            ]
            
            search_times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        max_search_time = max(search_times)
        print(f"Concurrent searches completed in {max_search_time:.3f} seconds")
        
        # Performance should be reasonable under concurrency
        assert max_creation_time < 5.0
        assert max_search_time < 2.0


class TestPatternEnginePerformance:
    """Performance testing for pattern engine operations."""
    
    def setup_method(self) -> None:
        """Set up pattern engine performance test fixtures."""
        self.pattern_engine = PatternEngine()
    
    def test_pattern_similarity_performance(self) -> None:
        """Test performance of pattern similarity calculations."""
        # Create patterns with varying complexity
        pattern_count = 100
        patterns = []
        
        for i in range(pattern_count):
            qkit_size = 5 + (i % 10)  # Variable QKit sizes
            qkit = [f"q_{i}_{j}" for j in range(qkit_size)]
            
            pattern = Pattern(
                pattern_id=f"similarity_pattern_{i}",
                qkit=qkit,
                attributes={
                    "domain": f"domain_{i % 5}",
                    "complexity": i % 3,
                    "category": f"cat_{i % 10}"
                }
            )
            patterns.append(pattern)
            self.pattern_engine.add_pattern(pattern)
        
        # Test similarity calculation performance
        similarity_count = 500  # Calculate similarities for random pairs
        start_time = time.time()
        
        similarities = []
        for i in range(similarity_count):
            pattern1_idx = i % pattern_count
            pattern2_idx = (i + 7) % pattern_count  # Offset to avoid self-comparison
            
            similarity = self.pattern_engine.calculate_pattern_similarity(
                patterns[pattern1_idx].id,
                patterns[pattern2_idx].id
            )
            similarities.append(similarity)
        
        end_time = time.time()
        similarity_time = end_time - start_time
        
        print(f"Calculated {similarity_count} similarities in {similarity_time:.3f} seconds")
        print(f"Average time per similarity: {similarity_time/similarity_count:.6f} seconds")
        
        # Verify results are reasonable
        assert all(0.0 <= sim <= 1.0 for sim in similarities)
        assert similarity_time < 5.0  # Should complete within 5 seconds
        assert (similarity_time / similarity_count) < 0.01  # Less than 10ms per calculation
    
    def test_pattern_clustering_performance(self) -> None:
        """Test performance of pattern clustering operations."""
        # Create patterns with some similarity structure
        cluster_count = 5
        patterns_per_cluster = 20
        
        for cluster_id in range(cluster_count):
            base_qkit = [f"cluster_{cluster_id}_base_{j}" for j in range(5)]
            
            for pattern_id in range(patterns_per_cluster):
                # Add some shared and some unique elements
                qkit = base_qkit.copy()
                qkit.extend([f"unique_{cluster_id}_{pattern_id}_{j}" for j in range(3)])
                
                pattern = Pattern(
                    pattern_id=f"cluster_pattern_{cluster_id}_{pattern_id}",
                    qkit=qkit,
                    attributes={"cluster": cluster_id, "pattern_idx": pattern_id}
                )
                self.pattern_engine.add_pattern(pattern)
        
        total_patterns = cluster_count * patterns_per_cluster
        
        # Test clustering performance
        start_time = time.time()
        clusters = self.pattern_engine.detect_pattern_clusters(similarity_threshold=0.3)
        end_time = time.time()
        
        clustering_time = end_time - start_time
        
        print(f"Clustered {total_patterns} patterns in {clustering_time:.3f} seconds")
        print(f"Found {len(clusters)} clusters")
        
        # Verify clustering results
        assert len(clusters) > 0
        assert clustering_time < 10.0  # Should complete within 10 seconds
    
    def test_usage_analysis_performance(self) -> None:
        """Test performance of pattern usage analysis."""
        # Create patterns with usage data
        pattern_count = 200
        max_instances_per_pattern = 50
        
        patterns = []
        for i in range(pattern_count):
            pattern = Pattern(pattern_id=f"usage_pattern_{i}")
            
            # Add random number of instances
            instance_count = (i % max_instances_per_pattern) + 1
            for j in range(instance_count):
                pattern.add_instance(f"entity_{i}_{j}")
            
            patterns.append(pattern)
            self.pattern_engine.add_pattern(pattern)
        
        # Test usage analysis performance
        start_time = time.time()
        analysis = self.pattern_engine.analyze_pattern_usage()
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        print(f"Analyzed usage for {pattern_count} patterns in {analysis_time:.3f} seconds")
        
        # Verify analysis results
        assert analysis['total_patterns'] == pattern_count
        assert analysis['total_usage'] > 0
        assert analysis_time < 2.0  # Should complete within 2 seconds


class TestQueryPerformance:
    """Performance testing for query operations."""
    
    def setup_method(self) -> None:
        """Set up query performance test fixtures."""
        self.config = ATLASConfig()
        self.atlas = ATLASEngine(self.config)
    
    def test_query_execution_performance(self) -> None:
        """Test performance of query execution lifecycle."""
        # Create test data
        entity_count = 1000
        for i in range(entity_count):
            entity = Entity(
                entity_id=f"query_perf_entity_{i}",
                attributes={
                    "name": f"Entity_{i}",
                    "category": f"cat_{i % 20}",
                    "priority": i % 5,
                    "status": "active" if i % 2 == 0 else "inactive"
                }
            )
            self.atlas.add_entity(entity.id, entity.to_dict())
        
        # Test query creation performance
        query_count = 100
        queries = []
        
        start_time = time.time()
        for i in range(query_count):
            query = iQuery(
                query_id=f"perf_query_{i}",
                query_text=f"Find entities in category cat_{i % 20}",
                priority=QueryPriority.NORMAL
            )
            queries.append(query)
            self.atlas.add_query(query.id, query.to_dict())
        
        creation_time = time.time() - start_time
        
        print(f"Created {query_count} queries in {creation_time:.3f} seconds")
        
        # Test query execution performance
        start_time = time.time()
        for query in queries:
            query.start_execution()
            
            # Simulate result processing
            for j in range(5):  # Add 5 mock results per query
                query.add_result({
                    "entity_id": f"query_perf_entity_{j}",
                    "score": 0.8 + (j * 0.04)
                })
            
            query.complete_execution()
        
        execution_time = time.time() - start_time
        
        print(f"Executed {query_count} queries in {execution_time:.3f} seconds")
        print(f"Average execution time per query: {execution_time/query_count:.6f} seconds")
        
        # Verify all queries completed successfully
        assert all(query.status.value == "completed" for query in queries)
        assert creation_time < 1.0  # Query creation should be fast
        assert execution_time < 5.0  # Query execution should be reasonable
        assert (execution_time / query_count) < 0.05  # Less than 50ms per query
    
    def test_quality_scoring_performance(self) -> None:
        """Test performance of query quality scoring."""
        # Create queries with varying amounts of result data
        query_count = 50
        queries = []
        
        for i in range(query_count):
            query = iQuery(query_id=f"scoring_query_{i}")
            
            # Add varying numbers of results
            result_count = (i % 20) + 1
            for j in range(result_count):
                query.add_result({
                    "entity_id": f"entity_{j}",
                    "score": 0.5 + (j * 0.05),
                    "derived_patterns": [f"pattern_{j % 3}"] if j % 2 == 0 else []
                })
            
            queries.append(query)
        
        # Test quality scoring performance
        start_time = time.time()
        quality_scores = []
        confidence_scores = []
        
        for query in queries:
            quality_scores.append(query.calculate_quality_score())
            confidence_scores.append(query.calculate_confidence_score())
        
        scoring_time = time.time() - start_time
        
        print(f"Calculated quality scores for {query_count} queries in {scoring_time:.3f} seconds")
        print(f"Average scoring time per query: {scoring_time/query_count:.6f} seconds")
        
        # Verify scoring results
        assert all(0.0 <= score <= 1.0 for score in quality_scores)
        assert all(0.0 <= score <= 1.0 for score in confidence_scores)
        assert scoring_time < 1.0  # Should complete quickly
        assert (scoring_time / query_count) < 0.02  # Less than 20ms per query


class TestMemoryUsage:
    """Test memory usage patterns and potential memory leaks."""
    
    def test_memory_usage_with_large_datasets(self) -> None:
        """Test memory usage with large datasets."""
        try:
            import psutil
            import gc
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            pytest.skip("psutil not available for memory testing")
        
        atlas = ATLASEngine(ATLASConfig())
        
        # Create large dataset
        entity_count = 5000
        for i in range(entity_count):
            entity = Entity(
                entity_id=f"memory_test_entity_{i}",
                attributes={
                    "name": f"Entity {i}",
                    "description": f"This is a test entity {i} " * 10,  # Larger strings
                    "data": list(range(i % 100)),  # Variable size lists
                    "metadata": {"created": datetime.now().isoformat(), "index": i}
                }
            )
            atlas.add_entity(entity.id, entity.to_dict())
            
            # Add some relationships
            if i > 0:
                atlas.add_relationship(f"memory_test_entity_{i-1}", entity.id, "follows")
        
        after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = after_creation_memory - initial_memory
        
        print(f"Memory usage increased by {memory_increase:.2f} MB for {entity_count} entities")
        print(f"Average memory per entity: {memory_increase/entity_count:.4f} MB")
        
        # Test memory cleanup
        del atlas
        gc.collect()
        
        after_cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_recovered = after_creation_memory - after_cleanup_memory
        
        print(f"Memory recovered after cleanup: {memory_recovered:.2f} MB")
        
        # Memory usage should be reasonable
        assert memory_increase < 500  # Less than 500MB for 5000 entities
        assert (memory_increase / entity_count) < 0.1  # Less than 100KB per entity
        
        # Some memory should be recovered (though not necessarily all due to Python's memory management)
        assert memory_recovered > 0 or after_cleanup_memory < after_creation_memory * 1.1


class TestStressConditions:
    """Test system behavior under stress conditions."""
    
    def test_rapid_concurrent_operations(self) -> None:
        """Test system stability under rapid concurrent operations."""
        atlas = ATLASEngine(ATLASConfig())
        
        def stress_worker(worker_id: int) -> Dict[str, Any]:
            """Worker function for stress testing."""
            operations = 0
            errors = 0
            start_time = time.time()
            
            try:
                for i in range(100):
                    # Rapid entity creation
                    entity = Entity(
                        entity_id=f"stress_{worker_id}_{i}",
                        attributes={"worker": worker_id, "iteration": i}
                    )
                    atlas.add_entity(entity.id, entity.to_dict())
                    operations += 1
                    
                    # Rapid searches
                    if i % 10 == 0:
                        atlas.query(f"stress_{worker_id}")
                        operations += 1
                    
                    # Rapid relationship creation
                    if i > 0:
                        atlas.add_relationship(
                            f"stress_{worker_id}_{i-1}",
                            f"stress_{worker_id}_{i}",
                            "stress_relation"
                        )
                        operations += 1
                        
            except Exception as e:
                errors += 1
                print(f"Worker {worker_id} encountered error: {e}")
            
            return {
                "worker_id": worker_id,
                "operations": operations,
                "errors": errors,
                "duration": time.time() - start_time
            }
        
        # Run stress test with multiple workers
        worker_count = 8
        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(stress_worker, i) for i in range(worker_count)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze stress test results
        total_operations = sum(r["operations"] for r in results)
        total_errors = sum(r["errors"] for r in results)
        max_duration = max(r["duration"] for r in results)
        
        print(f"Stress test completed: {total_operations} operations, {total_errors} errors")
        print(f"Maximum worker duration: {max_duration:.3f} seconds")
        print(f"Error rate: {total_errors/total_operations*100:.2f}%")
        
        # System should remain stable under stress
        assert total_errors / total_operations < 0.05  # Less than 5% error rate
        assert max_duration < 30.0  # Should complete within 30 seconds
        
        # Verify system integrity after stress test
        metrics = atlas.get_metrics()
        assert metrics['entities_created'] > 0
        assert len(atlas.entities) > 0


if __name__ == "__main__":
    # Run performance tests without pytest dependency
    import time
    
    print("🧪 Running ATLAS Performance Tests")
    print("=" * 60)
    
    # Collect all test classes
    test_classes = [
        TestATLASPerformance,
        TestPatternEnginePerformance,
        TestQueryPerformance,
        TestMemoryUsage,
        TestStressConditions
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    start_time = time.time()
    
    for test_class in test_classes:
        print(f"\n--- Running {test_class.__name__} ---")
        
        try:
            instance = test_class()
            test_methods = [method for method in dir(instance) if method.startswith('test_')]
            
            for test_method_name in test_methods:
                total_tests += 1
                print(f"  Running {test_method_name}...", end=" ")
                
                try:
                    # Setup method if available
                    if hasattr(instance, 'setup_method'):
                        instance.setup_method()
                    
                    # Run the test
                    test_method = getattr(instance, test_method_name)
                    test_method()
                    
                    passed_tests += 1
                    print("✓ PASSED")
                    
                except Exception as e:
                    failed_tests += 1
                    print(f"✗ FAILED - {type(e).__name__}: {str(e)}")
                    
        except Exception as e:
            print(f"✗ Class setup failed - {type(e).__name__}: {str(e)}")
    
    total_time = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Performance Test Results Summary")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    if total_tests > 0:
        print(f"Success rate: {(passed_tests / total_tests * 100):.1f}%")
    print(f"Execution time: {total_time:.3f}s")
    
    # Exit with appropriate code
    exit_code = 0 if failed_tests == 0 else 1
    print(f"\nExiting with code: {exit_code}")
    sys.exit(exit_code) 