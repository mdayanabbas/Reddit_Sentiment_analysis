library(dplyr)
library(ggplot2)
library("syuzhet")
library("tibble")

reddit_data <- read.csv("C:/Users/ayana/OneDrive/Desktop/ipl2.csv", stringsAsFactors = FALSE)


reddit_data <- select(reddit_data, -c(ID, Score, Total.Comments, Post.URL))

names(reddit_data) <- c("textID", "text", "selected_text", "sentiment")

head(reddit_data)
reddit_dataframe <- as.data.frame(reddit_data)
summary(reddit_data)

if (!require("pacman")) {
  install.packages("pacman")
}
pacman::p_load("scales", "tm", "RWeka", "wordcloud", "SentimentAnalysis", "syuzhet", "ggthemes")
library(pacman)
library(scales)
library(ggthemes)
library(tm)
library(NLP)
library(RWeka)
library(wordcloud)

thm <-  timechangethm <-  theme_wsj()+theme(
  plot.title = element_text(size = 20,hjust = 0.5),
  axis.text = element_text(size =16),
  axis.title = element_text(size = 16)
)

ggplot(data = reddit_data, aes(sentiment, fill = sentiment)) +
  geom_bar(aes(y = (..count..) / sum(..count..))) +
  geom_text(stat = "count", aes(y = (..count..) / sum(..count..), label = round((..count..) / sum(..count..), 2)), vjust = -1) +
  ggtitle(str_wrap("Tweets General Sentiment in Training Data", 30)) +
  thm +
  scale_y_continuous(labels = percent, limits = c(0, 1)) +
  ylab("Percent")







removeHtmlTags <- function(x) {
  (gsub("<.*?>", "", x))
}
removeHashTags <- function(x) {
  gsub("#\\S+", " ", x)
}
removeTwitterHandles <- function(x) {
  gsub("@\\S+", " ", x)
}
removeURL <- function(x) {
  gsub("http:[[:alnum:]]*", " ", x)
}
removeApostrophe <- function(x) {
  gsub("'", "", x)
}
removeNonLetters <- function(x) {
  gsub("[^a-zA-Z\\s]", " ", x)
}
removeSingleChar <- function(x) {
  gsub("\\s\\S\\s", " ", x)
}
cleanCorpus <- function(reviews) {
  # create the corpus
  corpus <- VCorpus(VectorSource(reviews))
  # remove reviews
  rm(reviews)
  # remove twitter handles and hashtags
  corpus <- tm_map(corpus, content_transformer(removeHtmlTags))
  corpus <- tm_map(corpus, content_transformer(removeHashTags))
  corpus <- tm_map(corpus, content_transformer(removeTwitterHandles))
  # other cleaning transformations
  corpus <- tm_map(corpus, content_transformer(removeURL))
  corpus <- tm_map(corpus, content_transformer(removeApostrophe))
  corpus <- tm_map(corpus, content_transformer(removeNonLetters))
  corpus <- tm_map(corpus, removeNumbers)
  corpus <- tm_map(corpus, content_transformer(tolower))
  corpus <- tm_map(corpus, removeWords, c(stopwords("english")))
  corpus <- tm_map(corpus, content_transformer(removeSingleChar))
  # Remove punctuations
  corpus <- tm_map(corpus, removePunctuation)
  # Eliminate extra white spaces
  corpus <- tm_map(corpus, stripWhitespace)
  # stem document
  corpuse <- tm_map(corpus, stemDocument)
  return(corpuse)
}

# function get word frequency
wordFrequency <- function(corpus) {
  dtm <- TermDocumentMatrix(corpus)
  rm(corpus)
  # convert to matrix
  m <- as.matrix(dtm)
  rm(dtm)
  # sort by word frequency
  v <- sort(rowSums(m), decreasing = TRUE)
  rm(m)
  # calculate word frequency
  word_frequencies <- data.frame(word = names(v), freq = v)
  return(word_frequencies)
}


# clean the tweets text
reviews <- reddit_data$text
corpus_train <- cleanCorpus(reviews)

reviews_selected_text <- reddit_data$selected_text
corpus_selected_text <- cleanCorpus(reviews_selected_text)
df_pos_train <- reddit_data[reddit_data$sentiment == "Positive",]
df_neg_train <- reddit_data[reddit_data$sentiment == "Negative",]
df_neu_train <- reddit_data[reddit_data$sentiment == "Neutral",]



corpus_train_pos <- cleanCorpus(df_pos_train$text)
corpus_train_neg <- cleanCorpus(df_neg_train$text)
corpus_train_neu <- cleanCorpus(df_neu_train$text)


word_frequencies_train <- wordFrequency(corpus_train)
# print top 10 word frequencies
head(word_frequencies_train, 10)

ggplot(data = word_frequencies_train[1:10, ], aes(reorder(word, order(freq, decreasing = TRUE)), freq)) +
  geom_col() +
  ggtitle("Top 10 most Frequent Words in Training Data") +
  xlab("Words") +
  ylab("Frequencies") +
  thm +
  theme(
    plot.title = element_text(size = 16, hjust = 0.5),
    axis.text = element_text(size = 14),
    axis.title = element_text(size = 14)
  )


set.seed(1234)
layout(matrix(c(1, 2), nrow = 2), heights = c(0.6, 4))
par(mar = rep(0, 4))
plot.new()
text(x = 0.5, y = 0.1, "Overall Tweets Wordcloud of Training Data")
wordcloud(
  words = word_frequencies_train$word, freq = word_frequencies_train$freq, min.freq = 10,
  max.words = 100, random.order = FALSE, rot.per = 0.35,
  colors = brewer.pal(8, "Set2")
)

word_freq_train_pos <- wordFrequency(corpus_train_pos)
# print top 10 word frequencies
head(word_freq_train_pos, 10)
word_freq_train_neg <- wordFrequency(corpus_train_neg)
# print top 10 word frequencies
head(word_freq_train_neg, 10)
word_freq_train_neu <- wordFrequency(corpus_train_neu)
# print top 10 word frequencies
head(word_freq_train_neu, 10)

set.seed(1234)
layout(matrix(c(1, 2), nrow = 2), heights = c(0.6, 4))
par(mar = rep(0, 4))
plot.new()
text(x = 0.5, y = 0.1, "Positive Tweets Wordcloud in Training Data")
wordcloud(
  words = word_freq_train_pos$word, freq = word_freq_train_pos$freq, min.freq = 10,
  max.words = 100, random.order = FALSE, rot.per = 0.35,
  colors = brewer.pal(8, "Set2")
)



set.seed(1234)
layout(matrix(c(1, 2), nrow = 2), heights = c(0.6, 4))
par(mar = rep(0, 4))
plot.new()
text(x = 0.5, y = 0.1, "Negative Tweets Wordcloud in Training Data")
wordcloud(
  words = word_freq_train_neg$word, freq = word_freq_train_neg$freq, min.freq = 10,
  max.words = 100, random.order = FALSE, rot.per = 0.35,
  colors = brewer.pal(8, "Set2")
)



set.seed(1234)
layout(matrix(c(1, 2), nrow = 2), heights = c(0.6, 4))
par(mar = rep(0, 4))
plot.new()
text(x = 0.5, y = 0.1, "Neutral Tweets Wordcloud in Training Data")
wordcloud(
  words = word_freq_train_neu$word, freq = word_freq_train_neu$freq, min.freq = 10,
  max.words = 100, random.order = FALSE, rot.per = 0.35,
  colors = brewer.pal(8, "Set2")
)



ggplot(data = word_freq_train_pos[1:10, ], aes(reorder(word, order(freq, decreasing = TRUE)), freq)) +
  geom_col() +
  ggtitle("Top 10 Positive Word by Frequencies in Training Data") +
  xlab("Words") +
  ylab("Frequencies") +
  thm +
  theme(
    plot.title = element_text(size = 16, hjust = 0.5),
    axis.text = element_text(size = 14),
    axis.title = element_text(size = 14)
  )


ggplot(data = word_freq_train_neg[1:10, ], aes(reorder(word, order(freq, decreasing = TRUE)), freq)) +
  geom_col() +
  ggtitle("Top 10 Negative Words by Frequency in Training Data") +
  xlab("Words") +
  ylab("Frequencies") +
  thm +
  theme(
    plot.title = element_text(size = 16, hjust = 0.5),
    axis.text = element_text(size = 14),
    axis.title = element_text(size = 14)
  )


ggplot(data = word_freq_train_neu[1:10, ], aes(reorder(word, order(freq, decreasing = TRUE)), freq)) +
  geom_col() +
  ggtitle("Top 10 Neutral Words by Frequency in Training Data") +
  xlab("Words") +
  ylab("Frequencies") +
  thm +
  theme(
    plot.title = element_text(size = 16, hjust = 0.5),
    axis.text = element_text(size = 14),
    axis.title = element_text(size = 14)
  )




sent_emotion <- get_nrc_sentiment(reddit_data$text)
sent_emotion_df <- as.data.frame(colSums(sent_emotion))
sent_emotion_df <- rownames_to_column(sent_emotion_df)
colnames(sent_emotion_df) <- c("emotion", "count")
ggplot(sent_emotion_df, aes(x = emotion, y = count, fill = emotion)) +
  geom_bar(stat = "identity") +
  thm +
  theme(legend.position = "none", panel.grid.major = element_blank()) +
  labs(x = "Emotion", y = "Total Count") +
  ggtitle("Sentiment of Overall Tweets in Training Data") +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_flip()



emotion_selected <- get_nrc_sentiment(reddit_data$selected_text)
emotion_df_selected <- as.data.frame(colSums(emotion_selected))
emotion_df_selected <- rownames_to_column(emotion_df_selected)
colnames(emotion_df_selected) <- c("emotion", "count")
ggplot(emotion_df_selected, aes(x = emotion, y = count, fill = emotion)) +
  geom_bar(stat = "identity") +
  thm +
  theme(legend.position = "none", panel.grid.major = element_blank()) +
  labs(x = "Emotion", y = "Total Count") +
  ggtitle("Sentiment of Overall Selected Text in Training Data") +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_flip()



emotion_pos <- get_nrc_sentiment(df_pos_train$selected_text)
emotion_pos <- as.data.frame(colSums(emotion_pos))
emotion_pos <- rownames_to_column(emotion_pos)
colnames(emotion_pos) <- c("emotion", "count")
ggplot(emotion_pos, aes(x = emotion, y = count, fill = emotion)) +
  geom_bar(stat = "identity") +
  thm +
  theme(legend.position = "none", panel.grid.major = element_blank()) +
  labs(x = "Emotion", y = "Total Count") +
  ggtitle("Sentiment of Positive Tweets in Training Data") +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_flip()




emotion_neg <- get_nrc_sentiment(df_neg_train$text)
emotion_neg <- as.data.frame(colSums(emotion_neg))
emotion_neg <- rownames_to_column(emotion_neg)
colnames(emotion_neg) <- c("emotion", "count")
ggplot(emotion_neg, aes(x = emotion, y = count, fill = emotion)) +
  geom_bar(stat = "identity") +
  thm +
  theme(legend.position = "none", panel.grid.major = element_blank()) +
  labs(x = "Emotion", y = "Total Count") +
  ggtitle("Sentiment of Negative Tweets in Training Data") +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_flip()



emotion_neu <- get_nrc_sentiment(df_neu_train$text)
emotion_neu <- as.data.frame(colSums(emotion_neu))
emotion_neu <- rownames_to_column(emotion_neu)
colnames(emotion_neu) <- c("emotion", "count")
ggplot(emotion_neu, aes(x = emotion, y = count, fill = emotion)) +
  geom_bar(stat = "identity") +
  thm +
  theme(legend.position = "none", panel.grid.major = element_blank()) +
  labs(x = "Emotion", y = "Total Count") +
  ggtitle("Sentiment of Neutral Tweets in Training Data") +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_flip()

