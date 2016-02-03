/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.mszankin.parallelclassifier.tools;

import com.mszankin.parallelclassifier.models.Article;
import com.sun.javafx.scene.control.skin.VirtualFlow;
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

/**
 *
 * @author maciek
 */
public class XMLArticleReader {

    public static List<Article> readAll(String path) {
        return XMLArticleReader.read(path, 0);
    }

    public static List<Article> read(String path, long limit) {
        if (limit < 0) {
            throw new IllegalArgumentException("Number of articles to parse cannot be less than zero. Value provided: " + limit);
        } else {
            List<Article> articles = new ArrayList<>();
            Article currentArticle = null;
            String tagContent = "";
            XMLInputFactory factory = XMLInputFactory.newInstance();
            XMLStreamReader reader;
            InputStream is;
            int articlesParsed = 0;

            try {
                is = new FileInputStream(path);
                reader = factory.createXMLStreamReader(is);

                while (reader.hasNext()) {
                    int event = reader.next();
                    switch (event) {
                        case XMLStreamConstants.START_ELEMENT:
                            if ("page".equals(reader.getLocalName())) {
                                currentArticle = new Article();
                            } else if ("text".equals(reader.getLocalName()) || "title".equals(reader.getLocalName())) {
                                tagContent = "";
                            }
                            break;
                        case XMLStreamConstants.CHARACTERS:
                            tagContent += reader.getText().trim();
                            break;
                        case XMLStreamConstants.END_ELEMENT:
                            switch (reader.getLocalName()) {
                                case "page":
                                    articles.add(currentArticle);
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
                            articles = new ArrayList<>();
                            break;
                    }
                    if (limit != 0 && articlesParsed >= limit) {
                        break;
                    }
                }
            } catch (XMLStreamException | FileNotFoundException ex) {
                Logger.getLogger(XMLArticleReader.class.getName()).log(Level.SEVERE, ex.toString());
            }
            
            return articles;
        }
    }
}
