/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.mszankin.parallelclassifier.models;

import com.mszankin.parallelclassifier.stemmer.Porter;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

/**
 *
 * @author maciek
 */
public class BagOfWords {

    private HashMap<String, Integer> bag;
    private double minimalWordFrequency;
    private int minimalWordLength;

    public BagOfWords(String text) {
        this(text.split(" "));
    }

    public BagOfWords(String[] words) {
        this.minimalWordFrequency = 0.005;
        this.minimalWordLength = 3;
        this.bag = new HashMap<>();
        
        Porter stemmer = new Porter();
        for (String word : words) {
            if (word.length() <= this.minimalWordLength) {
                continue;
            }
            stemmer.add(word.toCharArray(), word.length());
            stemmer.stem();
            word = stemmer.toString();

            Integer count = this.bag.get(word);
            this.bag.put(word, (count == null) ? 1 : count + 1);
        }
        this.bag = this.filterInsignificantWords(this.bag);
    }
    
    private HashMap<String, Integer> filterInsignificantWords(HashMap<String, Integer> bow){
        int numOfWords = 0;
        for (String key : bow.keySet()) {
            numOfWords += bow.get(key);
        }
        int value;
        HashMap<String, Integer> filtered = new HashMap<>();

        for (String key : bow.keySet()) {
            value = bow.get(key);
            if ((double) value / numOfWords > this.minimalWordFrequency) {
                filtered.put(key, value);
            }
        }

        return filtered;
    }

    //region Getters and setters
    public HashMap<String, Integer> getBag() {
        return bag;
    }
    //endregion

    //region Overrides
    @Override
    public String toString() {
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
        ValueComparator vc = new ValueComparator(this.bag);
        TreeMap<String, Integer> sortedMap = new TreeMap<>(vc);
        sortedMap.putAll(this.bag);
        return sortedMap.toString();
    }
    //endregion
}
