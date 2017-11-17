# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.sdk import Artifact
from qiime2.plugin.testing import TestPluginBase
from q2_fragment_insertion._insertion import sepp, classify_paths
import skbio
import pandas as pd
from pandas.testing import assert_frame_equal
from q2_types.feature_data import (AlignedDNASequencesDirectoryFormat,
                                   DNASequencesDirectoryFormat,
                                   DNAIterator)
from q2_types.tree import NewickFormat


class TestSepp(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_exercise_sepp(self):
        ar = Artifact.load(self.get_data_path('real_data.qza'))
        view = ar.view(DNASequencesDirectoryFormat)

        ar_refphylo = Artifact.load(self.get_data_path(
            'reference_phylogeny_small.qza'))
        ref_phylo_small = ar_refphylo.view(NewickFormat)

        ar_refaln = Artifact.load(self.get_data_path(
            'reference_alignment_small.qza'))
        ref_aln_small = ar_refaln.view(AlignedDNASequencesDirectoryFormat)

        obs_tree, obs_placements = sepp(
            view,
            reference_alignment=ref_aln_small,
            reference_phylogeny=ref_phylo_small)

        tree = skbio.TreeNode.read(str(obs_tree))
        obs = {n.name for n in tree.tips()}
        seqs = {r.metadata['id'] for r in ar.view(DNAIterator)}
        for seq in seqs:
            self.assertIn(seq, obs)

    def test_refmismatch(self):
        ar_refphylo = Artifact.load(self.get_data_path(
            'reference_phylogeny_small.qza'))
        ref_phylo_small = ar_refphylo.view(NewickFormat)

        ar_refaln = Artifact.load(self.get_data_path(
            'reference_alignment_small.qza'))
        ref_aln_small = ar_refaln.view(AlignedDNASequencesDirectoryFormat)

        with self.assertRaises(ValueError):
            sepp(None, reference_phylogeny=ref_phylo_small)

        with self.assertRaises(ValueError):
            sepp(None, reference_alignment=ref_aln_small)

        ar_refphylo_tiny = Artifact.load(self.get_data_path(
            'reference_phylogeny_tiny.qza'))
        ref_phylo_tiny = ar_refphylo_tiny.view(NewickFormat)

        with self.assertRaises(ValueError):
            sepp(None, reference_alignment=ref_aln_small,
                 reference_phylogeny=ref_phylo_tiny)


class TestClassify(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_classify_paths(self):
        ar_tree = Artifact.load(self.get_data_path('sepp_tree_tiny.qza'))
        ar_repseq = Artifact.load(self.get_data_path('real_data.qza'))

        obs_classification = classify_paths(
            ar_repseq.view(DNASequencesDirectoryFormat),
            ar_tree.view(NewickFormat))
        exp_classification = pd.read_csv(self.get_data_path(
            'taxonomy_real_data_tiny.tsv'), index_col=0, sep="\t").fillna("")
        assert_frame_equal(obs_classification, exp_classification)

        ar_tree_small = Artifact.load(
            self.get_data_path('sepp_tree_small.qza'))
        obs_classification_small = classify_paths(
            ar_repseq.view(DNASequencesDirectoryFormat),
            ar_tree_small.view(NewickFormat))
        exp_classification_small = pd.read_csv(self.get_data_path(
            'taxonomy_real_data_small.tsv'), index_col=0, sep="\t").fillna("")
        assert_frame_equal(obs_classification_small, exp_classification_small)

        ar_refphylo_tiny = Artifact.load(self.get_data_path(
            'reference_phylogeny_tiny.qza'))
        ref_phylo_tiny = ar_refphylo_tiny.view(NewickFormat)
        with self.assertRaises(ValueError):
            classify_paths(
                ar_repseq.view(DNASequencesDirectoryFormat), ref_phylo_tiny)


if __name__ == '__main__':
    unittest.main()
