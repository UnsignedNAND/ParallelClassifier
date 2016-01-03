/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.mszankin.parallelclassifier.clustering;

import com.mszankin.parallelclassifier.models.Article;
import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author maciek
 */
public class KMeans {
    private List<Article> articles;
    
    public KMeans(){
        this.articles = new ArrayList<>();
    }
    
    public KMeans(List<Article> articles){
        this.articles = articles;
    }

    //region Getters and setters
    public void setArticles(List<Article> articles) {
        this.articles = articles;
    }
    //endregion
}
