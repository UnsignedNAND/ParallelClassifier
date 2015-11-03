package clustering;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import parser.TextTools;
import clustering.models.Article;

public class KMeans {

    public final int kGroups = 20;
    List<Article> articles;
    List<Article> centers;
    
    public KMeans(List<parser.models.Article> articles){
        this.articles = new ArrayList<>();
        for(parser.models.Article article : articles){
            this.articles.add(new Article(article));
        }
    }

    public void InitializeGroupCenters() {
        this.centers = new ArrayList<>();
        while (this.centers.size() < this.kGroups) {
            int randomIndex = new Random().nextInt(this.articles.size());
            Article randomArticle = this.articles.get(randomIndex);
            if (!this.centers.contains(randomArticle)) {
                this.centers.add(randomArticle);
                System.out.println(randomArticle);
            }
        }
    }
    
    public void CalculateDistances(){
        for(Article article : this.articles){
            article.distances = new HashMap<>();
            for(Article center : this.centers){
                article.distances.put(center, TextTools.ComputeDistance(center.getBagOfWords(), article.getBagOfWords()));
            }
            System.out.println(article.getTitle() + " -> " + article.ClosestArticle().getTitle());
        }
    }
}
