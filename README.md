# P-RAG: Progressive Retrieval Augmented Generation For Planning on Embodied Everyday Task

# INSTALL
```bash
pip install -r requirements.txt
```

Note: orginaze the repository in the following file tree structure:
```
P-RAG
├── LLM-Planner # optional, need to be cloned from https://github.com/OSU-NLP-Group/LLM-Planner.git
├── alfworld # need to be cloned from https://github.com/alfworld/alfworld.git
├── db
├── log
├── utils
├── README.md
├── requirements.txt
└── ...
```

# RUN

fullfill the `run.sh` with valid api keys and run set the correct arguments.

```bash
bash run.sh
```

# CITE
```bibtex
@inproceedings{xu2024prag,
  title={P-RAG: Progressive Retrieval Augmented Generation For Planning on Embodied Everyday Task},
  author={Weiye Xu, Min Wang, Wengang Zhou, Houqiang Li},
  booktitle={ACM Multimedia},
  year={2024}
}
```
```