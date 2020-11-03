import scrappybara.config as cfg
from scrappybara.normalization.canonicalizer import Canonicalizer
from scrappybara.normalization.lemmatizer import Lemmatizer
from scrappybara.syntax.fixer import Fixer
from scrappybara.syntax.nodifier import Nodifier
from scrappybara.utils.files import load_dict_from_txt_file, load_set_from_txt_file
from scrappybara.utils.mutables import reverse_dict


class LabelledSentencePipeline(object):
    """Contains all steps to process a sentence that is already labelled"""

    def __init__(self, language_model):
        # Irregular lemmatization
        preterits = load_dict_from_txt_file(cfg.DATA_DIR / 'english' / 'irregular_preterits.txt')
        pps = load_dict_from_txt_file(cfg.DATA_DIR / 'english' / 'irregular_past_participles.txt')
        plurals = load_dict_from_txt_file(cfg.DATA_DIR / 'english' / 'irregular_plurals.txt')
        comps = load_dict_from_txt_file(cfg.DATA_DIR / 'english' / 'irregular_comparatives.txt')
        sups = load_dict_from_txt_file(cfg.DATA_DIR / 'english' / 'irregular_superlatives.txt')
        nouns = load_set_from_txt_file(cfg.DATA_DIR / 'english' / 'nouns.txt')
        adjs = load_set_from_txt_file(cfg.DATA_DIR / 'english' / 'adjectives.txt')
        reversed_pps = reverse_dict(pps)  # lemma => past participle
        # Pipeline
        self.__nodify = Nodifier()
        self._lemmatize = Lemmatizer(language_model, adjs, preterits, pps, plurals, comps, sups, reversed_pps)
        self.__fix = Fixer(adjs, nouns)
        self.__canonicalize = Canonicalizer(self._lemmatize)

    def _process_sentence(self, tokens, standards, tags, idx_tree):
        # Nofification
        node_dict, node_tree = self.__nodify(tokens, standards, tags, idx_tree)
        # Lemmatization
        for node in node_dict.values():
            node.lemma, node.suffix = self._lemmatize(node.standard, node.tag)
        # Fixing
        for node in node_dict.values():
            self.__fix(node, node_tree)
        # Canonicalization
        for node in node_dict.values():
            self.__canonicalize(node)
        return node_dict, node_tree
