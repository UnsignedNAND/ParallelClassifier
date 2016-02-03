package clustering;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import parser.TextTools;
import clustering.models.Article;
import java.util.AbstractList;

public class KMeans {

    public final int kGroups = 20;
    List<Article> articles;
    HashMap<Article, List<Article>> centers;

    public KMeans(List<parser.models.Article> articles) {
        this.articles = new ArrayList<>();
        for (parser.models.Article article : articles) {
            this.articles.add(new Article(article));
        }
    }

    public void InitializeGroupCenters() {
        this.centers = new HashMap<>();
        while (this.centers.size() < this.kGroups) {
            int randomIndex = new Random().nextInt(this.articles.size());
            Article randomArticle = this.articles.get(randomIndex);
            if (!this.centers.containsKey(randomArticle)) {
                this.centers.put(randomArticle, new ArrayList<>());
            }
        }
    }

    public void CalculateDistances() {
        for (Article article : this.articles) {
            article.distances = new HashMap<>();
            for (Article center : this.centers.keySet()) {
                article.distances.put(center, TextTools.ComputeDistance(center.getBagOfWords(), article.getBagOfWords()));
            }
//            System.out.println(article.getTitle() + " -> " + article.ClosestArticle().getTitle());
            this.centers.get(article.ClosestArticle()).add(article);
        }
    }

    public void CalculateNewCenters() {
        HashMap<Article, List<Article>> newCenters = new HashMap<>();
        HashMap<Article, List<Article>> tempCenters = this.centers;
        while (true) {
            for (Article centerArticle : this.centers.keySet()) {
                double groupDistanceSum = 0.0;
                double groupDistanceAvg = 0.0;
                System.out.println(centerArticle.getTitle());
                for (Article inClusterArticle : this.centers.get(centerArticle)) {
                    groupDistanceSum += inClusterArticle.getDistanceToCurrentCenter();
                    System.out.print("[" + inClusterArticle.getTitle() + " (" + inClusterArticle.getDistanceToCurrentCenter() + ")] ");
                }
                groupDistanceAvg = groupDistanceSum / this.centers.get(centerArticle).size();
                Article newCenterCandidate = this.GetArticleClosestToPoint(this.centers.get(centerArticle), groupDistanceAvg);
                System.out.println("");
                System.out.println("Distance = " + groupDistanceSum + "/" + this.centers.get(centerArticle).size() + "=" + groupDistanceAvg);
                System.out.println("New candidate: " + newCenterCandidate.getTitle() + "(" + newCenterCandidate.getDistanceToCurrentCenter() + ")");
                System.out.println("");
                newCenters.put(newCenterCandidate, new ArrayList<>());
            }
        }

    }

    private Article GetArticleClosestToPoint(List<Article> articles, double targetDistance) {
        double currentMinimal = Double.MAX_VALUE;
        Article articleClosestToPoint = null;
        for (Article article : articles) {
            if (Math.abs(article.getDistanceToCurrentCenter() - targetDistance) < currentMinimal) {
                currentMinimal = Math.abs(article.getDistanceToCurrentCenter() - targetDistance);
                articleClosestToPoint = article;
            }
        }
        return articleClosestToPoint;
    }
}
