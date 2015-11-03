/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package clustering.models;

import java.util.HashMap;

/**
 *
 * @author mszankin
 */
public class Article extends parser.models.Article{
    public HashMap<Article, Double> distances;
    private Double distanceToCurrentCenter = 0.0;

    public Double getDistanceToCurrentCenter() {
        return distanceToCurrentCenter;
    }
    
    public Article(){
        
    }
    
    public Article(parser.models.Article article){
        this.title = article.getTitle();
        this.text = article.getText();
        this.categoryWiki = article.getCategoryWiki();
        this.bagOfWords = article.getBagOfWords();
    }
    
    public Article ClosestArticle(){
        Article closestCenter = null;
        Double closestDistance = Double.MAX_VALUE;
        for(Article article : this.distances.keySet()){
            if(closestDistance > this.distances.get(article)){
                closestDistance = this.distances.get(article);
                closestCenter = article;
            }
        }
        this.distanceToCurrentCenter = closestDistance;
        return closestCenter;
    }
    
}
