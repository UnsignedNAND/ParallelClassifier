package parser;

import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import parser.models.Article;
import parser.stemmers.Porter;

public class TextTools {

    public static int minimalWordLength = 3;
    public static double minimalWordFrequency = 0.005;
    public static Locale locale = Locale.ENGLISH;

    /*
     Creates histogram with word length as key and number of such words in text 
     document as value
     */
    public static void WordsHistogram(Map<String, Integer> bagOfWords) {
        Map<Integer, Integer> histogram = new HashMap<>();
        for (String word : bagOfWords.keySet()) {
            int wordLength = word.length();
            int occurences = bagOfWords.get(word);

            Integer count = histogram.get(wordLength);
            histogram.put(wordLength, (count == null) ? occurences : count + occurences);
        }

        for (Integer key : histogram.keySet()) {
            System.out.println(key + " : " + histogram.get(key));
        }
    }

    public static void PrintBagOfWords(HashMap<String, Integer> map) {
        for (String key : map.keySet()) {
            System.out.println(key + " : " + map.get(key));
        }
        System.out.println("Len: " + map.size());
    }

    public static void PrintSortedBag(HashMap<String, Integer> map) {
        TreeMap<String, Integer> sortedMap = TextTools.SortWordsByOccurence(map);
        System.out.println(sortedMap);
    }

    public static void PrintArticles(List<Article> articles) {
        for (Article article : articles) {
            TextTools.PrintSortedBag(TextTools.cutInsignificantWords(article.getBagOfWords()));
//            TextTools.WordsHistogram(article.getBagOfWords());
            System.out.println("Size cut: " + TextTools.cutInsignificantWords(article.getBagOfWords()).size());
            System.out.println("Size bow: " + article.getBagOfWords().size());
        }
    }

    public static TreeMap<String, Integer> SortWordsByOccurence(HashMap<String, Integer> map) {
        class ValueComparator implements Comparator<String> {

            Map<String, Integer> map;

            public ValueComparator(Map<String, Integer> base) {
                this.map = base;
            }

            public int compare(String a, String b) {
                if (map.get(a) >= map.get(b)) {
                    return -1;
                } else {
                    return 1;
                }
            }
        }
        ValueComparator vc = new ValueComparator(map);
        TreeMap<String, Integer> sortedMap = new TreeMap<>(vc);
        sortedMap.putAll(map);
        return sortedMap;
    }

    public static HashMap<String, Integer> bagOfWords(String str) {
        HashMap<String, Integer> bow = new HashMap<>();
        Porter stemmer = new Porter();
        for (String word : str.split(" ")) {
            if (word.length() <= TextTools.minimalWordLength) {
                continue;
            }
            stemmer.add(word.toCharArray(), word.length());
            stemmer.stem();
            word = stemmer.toString();

            Integer count = bow.get(word);
            bow.put(word, (count == null) ? 1 : count + 1);
        }
        return bow;
    }

    public static int wordsInBagOfWords(HashMap<String, Integer> bow) {
        int num = 0;
        for (String key : bow.keySet()) {
            num += bow.get(key);
        }
        return num;
    }

    public static HashMap<String, Integer> cutInsignificantWords(HashMap<String, Integer> bow) {
        int numTotalWords = TextTools.wordsInBagOfWords(bow),
                value;
        HashMap<String, Integer> filtered = new HashMap<>();

        for (String key : bow.keySet()) {
            value = bow.get(key);
            if ((double) value / numTotalWords > TextTools.minimalWordFrequency) {
                filtered.put(key, value);
            }
        }

        return filtered;
    }

    public static String Simplify(String text) {
        text = TextTools.LowerString(text);
        text = TextTools.RemoveSpecialChars(text);
        text = TextTools.TrimWhiteSpaces(text);
        return text;
    }

    private static String RemoveSpecialChars(String str) {
        String specialCharsStr = ". , : ; ( ) [ ] < > ? / \\ \" * $ = + - _ { } ! @ # % ^ & \n ! ' |";

        for (String c : specialCharsStr.split(" ")) {
            str = str.replace(c, " ");
        }
        return str;
    }

    private static String TrimWhiteSpaces(String str) {
        str = str.replaceAll("^ +| +$|( )+", "$1");
        return str;
    }

    private static String LowerString(String str) {
        return str.toLowerCase(TextTools.locale);
    }
}
