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
    private BagOfWords textBag;
    private final Locale locale;
    
    public Article(String title, String text){
        this.locale = Locale.ENGLISH;
        this.title = title;
        this.text = title;
    }
    
    public Article(){
        this.locale = Locale.ENGLISH;
        this.title = null;
        this.text = null;
        this.textBag = null;
    }
    
    //region Tokenization
    private String simplify(String text) {
        text = this.lowerString(text);
        text = this.removeSpecialChars(text);
        text = this.trimWhiteSpaces(text);
        return text;
    }
    
    private String removeSpecialChars(String str) {
        return str.replaceAll("[^A-Za-z0-9 ]", " ");
    }

    private String trimWhiteSpaces(String str) {
        str = str.replaceAll("^ +| +$|( )+", "$1");
        return str;
    }

    private String lowerString(String str) {
        return str.toLowerCase(this.locale);
    }
    
    //endregion
    
    //region Getters and setters
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
        this.textBag = new BagOfWords(this.text);
    }
    //endregion
    
    //region Overrides
    @Override
    public String toString(){
        String r = this.title + " : " + this.textBag + "\n";
        return r;
    }
    //endregion
}
