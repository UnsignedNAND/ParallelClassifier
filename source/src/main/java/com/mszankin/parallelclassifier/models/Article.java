/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.mszankin.parallelclassifier.models;

import com.mszankin.parallelclassifier.stemmer.Porter;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;

/**
 *
 * @author maciek
 */
public class Article {
    private String title;
    private String text;
    private HashMap<String, Integer> textBag;
    private Locale locale = Locale.ENGLISH;
    private int minimalWordLength;
    
    public Article(String title, String text){
        this.title = title;
        this.text = title;
    }
    
    public Article(){
        this.title = null;
        this.text = null;
        this.textBag = null;
        this.minimalWordLength = 3;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = this.simplify(title);
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = this.simplify(text);
        this.textBag = this.bagOfWords(this.text);
    }
    
    private HashMap<String, Integer> bagOfWords(String text){
        HashMap<String, Integer> bow = new HashMap<>();
        Porter stemmer = new Porter();
        for (String word : text.split(" ")) {
            if (word.length() <= this.minimalWordLength) {
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
    
    //region Tokenization
    private String simplify(String text) {
        text = this.lowerString(text);
        text = this.removeSpecialChars(text);
        text = this.trimWhiteSpaces(text);
        return text;
    }
    
    private String removeSpecialChars(String str) {
        String specialCharsStr = ". , : ; ( ) [ ] < > ? / \\ \" * $ = + - _ { } ! @ # % ^ & \n ! ' |";

        for (String c : specialCharsStr.split(" ")) {
            str = str.replace(c, " ");
        }
        return str;
    }

    private String trimWhiteSpaces(String str) {
        str = str.replaceAll("^ +| +$|( )+", "$1");
        return str;
    }

    private String lowerString(String str) {
        return str.toLowerCase(this.locale);
    }
    
    //endregion
    
    //region Printing
    public void print(){
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
        ValueComparator vc = new ValueComparator(this.textBag);
        TreeMap<String, Integer> sortedMap = new TreeMap<>(vc);
        sortedMap.putAll(this.textBag);
        System.out.println(("Title: " + this.title ));
        System.out.println("BoW: " + sortedMap);
    }
    //endregion
}
