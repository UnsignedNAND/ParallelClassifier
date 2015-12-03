package com.mszankin.parallelclassifier.main;

import com.mszankin.parallelclassifier.models.Article;
import com.mszankin.parallelclassifier.tools.XMLArticleReader;
import java.util.List;
import java.util.concurrent.TimeUnit;

public class Msc {

    public static void main(String[] args) {
        long parseTimeStart = 0, parseTimeStop = 0, parseTimeDelta;

        parseTimeStart = System.nanoTime();
        Msc.execute();
        parseTimeStop = System.nanoTime();
        
        parseTimeDelta = parseTimeStop - parseTimeStart;
        System.out.println("Elapsed: " + TimeUnit.NANOSECONDS.toMillis(parseTimeDelta) + " ms");
    }
    
    private static void execute(){
        String path = "../data/simplewiki-20150314-pages-articles.xml";
        List<Article> articles = XMLArticleReader.read(path, 10);
        
        for(Article a : articles){
            System.out.println(a.getTitle());
            System.out.println(a.getText());
            System.out.println("==============================================");
        }
    }
}
