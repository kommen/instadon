(ns instadon.app
  (:require [babashka.fs :as fs]
            [babashka.http-client :as http]
            [cheshire.core :as json]
            [clojure.java.io :as io]
            [clojure.string :as str]

            [libpython-clj2.require :refer [require-python]]
            [libpython-clj2.python :refer [py. py.. py.-] :as py]))

(require-python
 :from "/opt/homebrew/Cellar/instaloader/4.14.1/libexec/lib/python3.13/site-packages"
 'instaloader)
(require-python 'itertools)
(require-python '[builtins :as py-builtins])

(defonce L
  (let [l (instaloader/Instaloader)]
    (py. l load_session_from_file "kommen")
    l))

(defn latest-post
  "Get the latest post from a given instagram profile by sorting the most recent ones by date."
  [profile-name]
  (let [profile (py. instaloader/Profile from_username (py.- L context) profile-name)
        posts-iterator (py. profile get_posts)
        ;; Fetch the 10 most recent posts. get_posts() usually returns a reverse-chronological iterator,
        ;; but pinned posts can appear first regardless of date.
        latest-posts-iter (itertools/islice posts-iterator 10)
        ;; Filter out pinned posts, then convert the resulting iterator to a Clojure vector.
        unpinned-posts (py/->jvm (py-builtins/filter (fn [p] (not (py.- p is_pinned)))
                                                     latest-posts-iter))
        #_#_sorted-posts (sort-by #(py.- % date_utc) > unpinned-posts)]
    unpinned-posts))

(comment
  (def post (py. instaloader/Post from_shortcode (py.- L context) "DJeNLlxxTHl"))
  (py.- post date_utc)

  (py.- post caption)
  (let [profile (py. instaloader/Profile from_username (py.- L context) "kulturneubau")
        posts (py. profile get_posts)]
    posts)

  ;; Example usage of the new function
  (let [latest (latest-post "kulturneubau")]
    (def lp latest))

  (py.- lp date_utc)
  )


(def json-headers {:accept "application/json"
                   :content-type "application/json"})

(def config
  {:mastodon {:instance "https://neubau.social"
              :access-token "czPVtqZUvT5RvxTE_KVygunCiupXxre-71SBIndYf_o"}})



(defn create-mastodon-draft
  "Create a draft post in Mastodon"
  [status media-ids visibility]
  (let [url (str (get-in config [:mastodon :instance]) "/api/v1/statuses")
        params {:status status
                :media_ids media-ids
                :visibility visibility
                :draft true}
        headers {"Authorization" (str "Bearer " (get-in config [:mastodon :access-token]))}]
    (http/post url {:headers (merge json-headers
                                    headers)
                    :body (json/encode params)})))

(comment
  (create-mastodon-draft "TEST" [114485373086948381] "public")
  )

(defn upload-media-to-mastodon
  "Upload media to Mastodon"
  [content description]
  (let [url (str (get-in config [:mastodon :instance]) "/api/v2/media")
        headers {"Authorization" (str "Bearer " (get-in config [:mastodon :access-token]))}]
    (-> (http/post
         url
         {:headers headers
          :multipart [{:name "file" :content content}
                      {:name "description" :content description}]})
        :body
        (json/parse-string true)
        :id)))


(comment
  (upload-media-to-mastodon (io/input-stream (.getBytes (:body r)))
                            "TEST"))

(defn url->file [url]
  (let [tmpfile (fs/create-temp-file {:suffix ".jpeg"})
        file (io/file (.toString tmpfile))]
    (io/copy (-> url (http/get {:as :bytes}) :body)
             file)
    file))

(defn download [url]
  (-> (http/post "https://cobalt.uber.space/"
                 {:headers json-headers
                  :body (json/encode {:url url})})
      :body
      (json/parse-string true)))


(defn process [result]
  (case (:status result)
    "picker"
    (->> result
         :picker
         (filter #(= "photo" (:type %)))
         (map (comp url->file :url)))
    "tunnel"
    [(url->file (:url result))]))



(comment
  (process (download "https://www.instagram.com/p/DJeNLlxxTHl/"))

  (download "https://www.instagram.com/p/DI3AcneMlZW/")

  (io/input-stream (-> (download "https://www.instagram.com/kulturneubau/p/DJeNLlxxTHl/")
                       :picker
                       first
                       :url
                       (http/get {:as :bytes})
                       :body))
  (upload-media-to-mastodon
   (let [tmpfile (fs/create-temp-file {:suffix ".jpeg"})
         file (io/file (.toString tmpfile))]
     (io/copy (-> (download "https://www.instagram.com/kulturneubau/p/DJeNLlxxTHl/")
                  :picker
                  first
                  :url
                  (http/get {:as :bytes})
                  :body)
              file)
     file)


   "TEST")


  )
