/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.mszankin.parallelclassifier.models;

import java.util.Locale;

/**
 *
 * @author maciek
 */
public class Article {
    private String title;
    private String text;
    public static Locale locale = Locale.ENGLISH;
    
    public Article(String title, String text){
        this.title = title;
        this.text = title;
    }
    
    public Article(){
        this.title = null;
        this.text = null;
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
    }
    
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
        return str.toLowerCase(Article.locale);
    }
}
