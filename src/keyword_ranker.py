import rake
from collections import defaultdict
import operator

def txt_reader(file_txt, encoding='utf-8'):
    file_obj = open(file_txt, 'r', encoding=encoding)
    text = file_obj.read()
    return text

class KeywordRanker(object):
    def __init__(self, min_chars=1, max_words=3, min_occurances=1, stopwords_txt='smartstoplist.txt'):
        self.stopwords_txt = stopwords_txt
        self.max_words = max_words
        self.min_chars = min_chars
        self.min_occurances = min_occurances
        self.corpus_keywords = None


    def fit(self, corpus_txt, encoding='utf-8'):
        rake_object = rake.Rake(self.stopwords_txt, self.min_chars,
                            self.max_words, self.min_occurances)
        text = txt_reader(corpus_txt, encoding=encoding)
        self.corpus_keywords = rake_object.run(text)


    def wordscores(self, transcript_txt, encoding='utf-8', min_chars=1,
                    max_words=3, min_occurances=1):
        text = txt_reader(transcript_txt, encoding=encoding)
        sentencelist = rake.split_sentences(text)
        stopwordpattern = rake.build_stop_word_regex(self.stopwords_txt)
        phraselist = rake.generate_candidate_keywords(sentencelist,
                            stopwordpattern, min_chars, max_words)
        wordscores = rake.calculate_word_scores(phraselist)
        return wordscores


    def rank(self, n, *transcripts, encoding='utf-8'):
        '''Scores the ton n corpus keywords with a wordscores list.'''
        top_n_corpus = [word[0] for word in self.corpus_keywords[:n]]
        keyword_scores = defaultdict(int)
        n_transcripts = len(transcripts)
        for transcript in transcripts:
            wordscores = self.wordscores(transcript, encoding=encoding)
            for keyword in top_n_corpus:
                keyword_score = 0
                for word in keyword.split(' '):
                    try:
                        keyword_score += wordscores[word]/n_transcripts
                    except KeyError:
                        pass
                keyword_scores[keyword] += keyword_score
        keyword_rank = [(key, keyword_scores[key]) for key in sorted(keyword_scores,
                key=keyword_scores.get, reverse = True)]
        keyword_deviation = self.get_deviation(keyword_rank, n)
        return keyword_rank, keyword_deviation


    def get_deviation(self, keyword_rank, n):
        kwr_sorted = sorted(keyword_rank)
        ckw_sorted = sorted(self.corpus_keywords[:n])
        keyword_deviation = [(kwr_sorted[i][0], (kwr_sorted[i][1]-ckw_sorted[i][1])
                            / ckw_sorted[i][1]) for i in range(n)]
        keyword_deviation_unsorted = sorted(keyword_deviation, )
        kw_zipped = zip(keyword_deviation, kwr_sorted)
        kw_zipped_sorted = sorted (kw_zipped, key=lambda x: -x[1][1])
        keyword_deviation = [kw[0] for kw in kw_zipped_sorted]
        return keyword_deviation


if __name__ == '__main__':
    stopwords = '/Users/stefandecker/Coding/RAKE-tutorial/SmartStoplist.txt'
    corpus = '/Users/stefandecker/Coding/keyword_ranker/data/script.txt'
    transcript1 = '/Users/stefandecker/Coding/keyword_ranker/data/transcript_1.txt'
    transcript2 = '/Users/stefandecker/Coding/keyword_ranker/data/transcript_2.txt'
    transcript3 = '/Users/stefandecker/Coding/keyword_ranker/data/transcript_2.txt'



    kwr = KeywordRanker(2, 3, 3)
    kwr.fit(corpus)
    # keywords, top_n = kwr.rank(15, transcript1, transcript2, transcript3)
    keyword_rank, keyword_deviation = kwr.rank(15, transcript1, transcript2, transcript3)
