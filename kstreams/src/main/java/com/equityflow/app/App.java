package com.equityflow.app;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.utils.Bytes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Materialized;
import org.apache.kafka.streams.kstream.Produced;
import org.apache.kafka.streams.kstream.Aggregator;
import org.apache.kafka.streams.kstream.TimeWindows;
import org.apache.kafka.streams.kstream.Windowed;
import org.apache.kafka.streams.state.WindowStore;
import org.apache.kafka.streams.kstream.WindowedSerdes;
import java.time.Duration;


import java.util.Properties;
import java.util.concurrent.CountDownLatch;
import org.json.JSONObject;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;


public class App{
    public static void main(String[] args) throws Exception{
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "streams-avgStock");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:29092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);

        final StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> source = builder.stream("stock_price");
        Duration windowSize = Duration.ofSeconds(30);
        Duration advanceBy = Duration.ofSeconds(30);
        TimeWindows timeWindows = TimeWindows.of(windowSize).advanceBy(advanceBy);

        Serde<Windowed<String>> windowedStringSerde = WindowedSerdes.timeWindowedSerdeFrom(String.class);


        source.groupByKey()
        .windowedBy(timeWindows)
        .aggregate(
            ()->{                                                                                                                                                   //Initializer
                    JSONObject stock_avg = new JSONObject();
                    stock_avg.put("avg",  0);
                    stock_avg.put("count", 0);
                    stock_avg.put("timestamp", 0);
                    return stock_avg.toString();
            }   
            ,
            new Aggregator<String, String, String>(){
                @Override
                public String apply(final String Key, final String value, String aggregate){
                    
                    JSONObject aggregate_ = new JSONObject(aggregate);
                    long count_ = aggregate_.getLong("count");
                    double avg_ = aggregate_.getDouble("avg");
                    //double avg_=0;

                    JSONObject stock_info = new JSONObject(value);
                    double close_price = stock_info.getDouble("close");
                    double timestamp = stock_info.getLong("timestamp");

                    double sum_ = (avg_ * count_) + close_price;
                    count_++;
                    avg_ = sum_ / (double)count_;

                    JSONObject stock_avg = new JSONObject();
                    stock_avg.put("avg", avg_);
                    stock_avg.put("timestamp", timestamp);
                    stock_avg.put("count", count_);
                    return stock_avg.toString();

                    

                }
            },
            Materialized.<String, String,  WindowStore<Bytes, byte[]>>as("avg-state-store")



        ).mapValues((aggregate)-> {
            JSONObject stock_avg_info = new JSONObject(aggregate);
            double avg = stock_avg_info.getDouble("avg");
            long timestamp = stock_avg_info.getLong("timestamp");

            LocalDateTime dateTime = LocalDateTime.ofInstant(Instant.ofEpochSecond(timestamp), ZoneId.systemDefault());

            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            String timestampStr = dateTime.format(formatter);
           
            JSONObject stock_avg = new JSONObject();
            stock_avg.put("avg", avg);
            stock_avg.put("timestamp", timestampStr);
            return stock_avg.toString();
        })
        //.Materialized.<String, Double, KeyValueStore<Bytes, byte[]>>as("avg-store")
        .toStream().to("stocks_avg_output", Produced.with(windowedStringSerde, Serdes.String()));

        
        final Topology topology = builder.build();
        final KafkaStreams streams = new KafkaStreams(topology, props);
        streams.cleanUp();
        //System.out.println(topology.describe());

        final CountDownLatch latch = new CountDownLatch(1);

        // attach shutdown handler to catch control-c
        Runtime.getRuntime().addShutdownHook(new Thread("streams-shutdown-hook") {
            @Override
            public void run() {
                streams.close();
                latch.countDown();
            }
        });

        try {
            streams.start();
            latch.await();
        } catch (Throwable e) {
            System.exit(1);
        }
        System.exit(0);
    }

    
    }
