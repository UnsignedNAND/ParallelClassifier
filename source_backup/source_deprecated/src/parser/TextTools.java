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
        double distance = 0.0;
        HashMap<String, Integer> document1 = null;
        HashMap<String, Integer> document2 = null;
        for (Article article : articles) {
            document1 = TextTools.CutInsignificantWords(article.getBagOfWords());
            document2 = null;
            
            for (Article articleToCompare : articles) {
//                if(!articleToCompare.getTitle().equals(article.getTitle())){
                    document2 = TextTools.CutInsignificantWords(articleToCompare.getBagOfWords());
                    distance = TextTools.ComputeDistance(document1, document2);
                    System.out.println(article.getTitle() + " x " + articleToCompare.getTitle() + " = " + distance);
//                }
            }
            System.out.println("*******************************");
//            TextTools.WordsHistogram(article.getBagOfWords());
//            System.out.println("Size cut: " + TextTools.CutInsignificantWords(article.getBagOfWords()).size());
//            System.out.println("Size bow: " + article.getBagOfWords().size());
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

    public static int WordsInBagOfWords(HashMap<String, Integer> bow) {
        int num = 0;
        for (String key : bow.keySet()) {
            num += bow.get(key);
        }
        return num;
    }

    public static HashMap<String, Integer> CutInsignificantWords(HashMap<String, Integer> bow) {
        int numTotalWords = TextTools.WordsInBagOfWords(bow),
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

    public static int InnerProduct(HashMap<String, Integer> document1, HashMap<String, Integer> document2) {
        int sum = 0;

        for (String word : document1.keySet()) {
            if (document2.containsKey(word)) {
                sum += document1.get(word) * document2.get(word);
            }
        }
        return sum;
    }

    public static double ComputeDistance(HashMap<String, Integer> document1, HashMap<String, Integer> document2) {
        int numerator = TextTools.InnerProduct(document1, document2);
        double denominator = Math.sqrt(TextTools.InnerProduct(document1, document1) * TextTools.InnerProduct(document2, document2));

        return Math.acos(numerator / denominator);
    }
}
