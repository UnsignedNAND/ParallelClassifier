package parser;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;
import parser.models.Article;

public class WikiParser {

    String path = "../data/simplewiki-20150314-pages-articles.xml";


    List<Article> articles;
    Article currentArticle;
    String tagContent = "";

    XMLInputFactory factory = XMLInputFactory.newInstance();
    XMLStreamReader reader;

    public WikiParser() {
        try {
            InputStream is = new FileInputStream(path);
            this.reader = factory.createXMLStreamReader(is);
        } catch (XMLStreamException | FileNotFoundException ex) {
            Logger.getLogger(WikiParser.class.getName()).log(Level.SEVERE, ex.toString());
        }
        this.articles = new ArrayList<>();
    }
    
    public void PrintList(){
        for(Article article : this.articles){
//            System.out.println(article);
//            article.PrintBag();
            TextTools.WordsHistogram(article.getBagOfWords());
        }
    }

    public void Parse() {
        int articlesParsed = 0;
        try {
            while (reader.hasNext()) {
                int event = reader.next();
                switch (event) {
                    case XMLStreamConstants.START_ELEMENT:
                        if ("page".equals(reader.getLocalName())) {
                            currentArticle = new Article();
                        }
                        else if ("text".equals(reader.getLocalName()) || "title".equals(reader.getLocalName())) {
                            tagContent = "";
                        }
                        break;
                    case XMLStreamConstants.CHARACTERS:
                        tagContent += reader.getText().trim();
                        break;
                    case XMLStreamConstants.END_ELEMENT:
                        switch (reader.getLocalName()) {
                            case "page":
                                this.articles.add(currentArticle);
                                articlesParsed += 1;
                                break;
                            case "title":
                                currentArticle.setTitle(tagContent);
                                tagContent = "";
                                break;
                            case "text":
                                currentArticle.setText(tagContent);
                                tagContent = "";
                                break;
                        }
                        break;
                        
                    case XMLStreamConstants.START_DOCUMENT:
                        this.articles = new ArrayList<>();
                        break;
                }
                if(articlesParsed >= 1){
                        break;
                    }
            }
        } catch (XMLStreamException ex) {
            Logger.getLogger(WikiParser.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
