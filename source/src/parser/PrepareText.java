package parser;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class PrepareText {

    public static String Stemm(String word) {
        return "";
    }

    public static Map<String, Integer> bagOfWords(String str) {
        Map<String, Integer> bow = new HashMap<>();
        for (String word : str.split(" ")) {
            if(word.length() <= 3){
                continue;
            }
            Integer count = bow.get(word);
            bow.put(word, (count == null) ? 1 : count + 1);
        }
        return bow;
    }

    public static String RemoveSpecialChars(String str) {
        String specialCharsStr = ". , : ; ( ) [ ] < > ? / \\ \" * $ = + - _ { } ! @ # % ^ & \n ! ' |";

        for (String c : specialCharsStr.split(" ")) {
            str = str.replace(c, " ");
        }
        return str;
    }

    public static String TrimWhiteSpaces(String str) {
        str = str.replaceAll("^ +| +$|( )+", "$1");
        return str;
    }

    public static String LowerString(String str) {
        return str.toLowerCase(Locale.ENGLISH);
    }
}
