package parser.models;

import java.util.Map;
import parser.PrepareText;
import parser.stemmers.Porter;

public class Article {

    private String title;
    private String text;
    private Map<String, Integer> bagOfWords;

    private final Porter stemmer;

    public Map<String, Integer> getBagOfWords() {
        return bagOfWords;
    }
    private String categoryWiki;

    public Article() {
        this.stemmer = new Porter();
    }

    @Override
    public String toString() {
        return "Title: " + this.title + "\nText:\n" + this.text + "\n********************";
    }

    public void PrintBag() {
        for (String key : this.bagOfWords.keySet()) {
            System.out.println(key + " : " + this.bagOfWords.get(key));
        }
        System.out.println("Len: " + this.bagOfWords.size());
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        text = PrepareText.LowerString(text);
        text = PrepareText.RemoveSpecialChars(text);
        text = PrepareText.TrimWhiteSpaces(text);
        this.text = text;
        String text2 = "";
        for (String word : text.split(" ")) {
            this.stemmer.add(word.toCharArray(), word.length());
            this.stemmer.stem();
            text2 += this.stemmer.toString() + " ";
        }
        text = text2;
        this.bagOfWords = PrepareText.bagOfWords(text);
    }

    public String getCategoryWiki() {
        return categoryWiki;
    }

    public void setCategoryWiki(String categoryWiki) {
        this.categoryWiki = categoryWiki;
    }
}
