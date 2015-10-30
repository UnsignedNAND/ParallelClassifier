package parser;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import parser.stemmers.Porter;

public class TextTools {

    /*
    Creates histogram with word length as key and number of such words in text 
    document as value
    */
    public static void WordsHistogram(Map<String, Integer> bagOfWords){
        Map<Integer, Integer> histogram = new HashMap<>();
        for(String word : bagOfWords.keySet()){
            int wordLength = word.length();
            int occurences = bagOfWords.get(word);
            
            Integer count = histogram.get(wordLength);
            histogram.put(wordLength, (count == null) ? occurences : count + occurences);
        }

        for(Integer key : histogram.keySet()){
            System.out.println(key + " : " + histogram.get(key));
        }
    }

    public static Map<String, Integer> bagOfWords(String str) {
        Map<String, Integer> bow = new HashMap<>();
        Porter stemmer = new Porter();
        for (String word : str.split(" ")) {
            if(word.length() <= 3){
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

    public static String Simplify(String text){
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
        return str.toLowerCase(Locale.ENGLISH);
    }
}
