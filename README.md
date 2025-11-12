# Polish Wikipedia Speedrun Solver

A small web app inspired by the **Wikipedia Speedrun game** and the classic **Six Degrees of Wikipedia** website.  
It explores the idea that every Wikipedia article is connected — and asks:  
**how closely linked are two seemingly unrelated topics?**

---

## Purpose

The project is built around a simple question:  
> “How many clicks separate one Polish Wikipedia article from another?”

It demonstrates how the network structure of Wikipedia can be modeled as a graph,  
where articles are **nodes** and hyperlinks are **edges**.  
By finding the shortest path between two pages, the app reveals how tightly woven our collective knowledge really is.

---

## Try it

In order to run the application yourself, you need to get the dataset. There are 2 main ways to get the dataset yourself:

1. Directly download the dataset from [huggingface](https://huggingface.co/datasets/dziura0623/plwiki/tree/main),
where the dataset is located.
After downloading the dataset, just paste it into the **dataset** directory, inside the project files. After that,
run the **app.py** code, and the application is ready to be used!
2. If you are interested in creating the dataset yourself or modify it somehow, you can download and 
run the  **properScript.sh** file, which creates the dataset from scratch. You can also change the language of the dumps, 
so you can create the database in any other language that wikipedia supports. 

**WARNING!** The script runs for a long time, if you don't have a powerful machine, so you might want to use the 
google compute Virtual machines ([sdow repository](https://github.com/jwngr/sdow) helped me a lot with this)

---
##  Inspiration

- **Wikipedia Speedrun** — a popular game where players race through hyperlinks from one article to another as fast as possible.  
  This project takes that idea and automates it, finding the shortest possible route instead of relying on speed or luck.

- **Six Degrees of Wikipedia** — a website that explores the “small-world” nature of Wikipedia’s link graph,  
  showing how any two pages are rarely more than a few steps apart.  
  This app brings that concept to the **Polish Wikipedia**, offering a local and linguistic twist on the same idea.

---

## What It Represents

Beyond just a fun experiment, the project reflects how **knowledge is interconnected**.  
Every article — from *Polska* to *Kawa* — lives inside a web of references and associations.  
Exploring these links highlights:
- how humans organize information,  
- how topics cluster together,  
- and how the structure of Wikipedia mirrors the structure of thought.

---


## Credits

- [Six Degrees of Wikipedia](https://www.sixdegreesofwikipedia.com/)
Original Wikipedia speedrun website, which was the main inspiration and source of help for this project.
- [Jacob Wegner](https://github.com/jwngr)
Author of the above project. A lot of data creation code comes from his repository, so check his work out, it was really helpful for me!


---

## Author

**Radosław Gersz**, radekgersz@gmail.com

Uppsala University — Data Science Student

This project was created as a side exploration of the structure of knowledge,  
combining curiosity, data, and the love of clicking random blue links on Wikipedia.

---

## License

MIT License — open to explore, remix, and improve.
