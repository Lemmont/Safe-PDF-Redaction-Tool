# Logbook

### 26 Oct '23

https://www.rijksoverheid.nl/onderwerpen/wet-open-overheid-woo
https://link.springer.com/chapter/10.1007/978-3-031-43849-3_28
https://books.google.nl/books?hl=en&lr=&id=HK7YEAAAQBAJ&oi=fnd&pg=PA310&dq=redacted+text+recognition+&ots=vAhoTFLm48&sig=hN3cESzDT3y9vU7uMV9j54SpAX4&redir_esc=y#v=onepage&q=redacted%20text%20recognition&f=false


#### meeting met Maarten en Gensi


popluar, xpdf
donderdag planning inleveren.
schrijven en praktijk tegelijkertijd

### 25 Oct '23

#### [What are rule based systems?](https://www.scaler.com/topics/rule-based-system-in-ai/)

- AI bases choices or inferences on established rules.
- Expert and decision support systems?
- **Relies on a collection of predetermined rules to decide what to do next.**
- Rules are written in 'simple' human language for easy troubleshoot and maintance.
- Given a set of inputs, RBS will always create the same output; predictable and dependable; **determinism**
- **Scalable**
- Can be modified or updated more easily because rules can be divided into smaller components.
- Collection of inputs + rules = output.

Rule based systems consist of seven fundamental elements

- Knowledge base: rules; IF(cond) THEN(action).
- Database: collection of facts compared to the knowledge base's rules if (cond.) clause.
- The inference engine: derive logic and arrive at a conclusion; connect the facts from the database with the rules specified in the knowledge base; semantic reasoner; match-resolve-act loop.

- Explanations facilities

- User interface

- External connection

- Active recall

https://link.springer.com/chapter/10.1007/978-3-031-43849-3_28

Imagnet:

> ImageNet is an image database organized according to the WordNet hierarchy (currently only the nouns), in which each node of the hierarchy is depicted by hundreds and thousands of images. The project has been instrumental in advancing computer vision and deep learning research. The data is available for free to researchers for non-commercial use.

> ImageNet is an image dataset organized according to the WordNet hierarchy. Each meaningful concept in WordNet, possibly described by multiple words or word phrases, is called a "synonym set" or "synset". There are more than 100,000 synsets in WordNet; the majority of them are nouns (80,000+). In ImageNet, we aim to provide on average 1000 images to illustrate each synset. Images of each concept are quality-controlled and human-annotated. In its completion, we hope ImageNet will offer tens of millions of cleanly labeled and sorted images for most of the concepts in the WordNet hierarchy.

Image segmentation, semantic segmentation, instance segmentation.

**Semantic segmentation is important**; the process of classifying areas of interest in an image on a pixel-level basis. [a similiar example](https://medium.com/@kennethcassel/using-machine-learning-to-redact-personal-identifying-information-b95b53b935a9). You create a mask or map image and pass it into a deep learning model along-side the original image. Model learns from this labeled data and be able to predict what pixels in a new image are; training data used to pass into neural models to recognize redacted text in provided image.
[example](https://www.youtube.com/watch?v=uiE56h5LyXc). **Training data to train our neural model(s) and a dataset to test it on.**

**Semantic segmentation overview [link](https://www.youtube.com/watch?v=uiE56h5LyXc)**.

1. label your data
2. Create two datastores
3. Partition datastores (train, test)
4. import pretrained model and modify it
5. Train and evaluate

**[hard negative examples](https://www.reddit.com/r/computervision/comments/2ggc5l/what_is_hard_negative_mining_and_how_is_it/)**:

> Let's say I give you a bunch of images that contain one or more people, and I give you bounding boxes for each one. Your classifier will need both positive training examples (person) and negative training examples (not person).
> For each person, you create a positive training example by looking inside that bounding box. But how do you create useful negative examples?
> A good way to start is to generate a bunch of random bounding boxes, and for each that doesn't overlap with any of your positives, keep that new box as a negative.
> Ok, so you have positives and negatives, so you train a classifier, and to test it out, you run it on your training images again with a sliding window. But it turns out that your classifier isn't very good, because it throws a bunch of false positives (people detected where there aren't actually people).
> **A hard negative is when you take that falsely detected patch, and explicitly create a negative example out of that patch, and add that negative to your training set. When you retrain your classifier, it should perform better with this extra knowledge, and not make as many false positives.**

### Plan

1. Creating dataset; looking for pre-labeld datasets; creating our own handlabelled images (labelbox and then creating one mask image using Pillow).

2. Train an existing model [this one](https://huggingface.co/tasks/image-segmentation)

3. Test data

4. Evaluate

5. ...

### Questions

- Object detection, image/semantic segmentation, panoptic segmentation?
