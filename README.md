# Translator
Tool to translate NLP datasets with ease. Keeps track of character count and passed time since last session, so that you do not exceed free character limit.

# Usage
```bash
git clone https://github.com/emrecncelik/dataset_translator.git
cd dataset_translator

python translate_txt.py --input "dataset.txt" --output "dataset_translated.txt"
```

```
$ python translate_txt.py --help
usage: translate_txt.py [-h] --input str --output str
                        [--source str] [--target str]
                        [--credentials str] [--save_every int]
                        [--logfile str] [--loglevel str]
                        [--inline_separator str]

mandatory arguments:
  --input str           input data file path (default: None)
  --output str          output data file path (default: None)

optional arguments:
  -h, --help            show this help message and exit

  --source str          language of input data (default: en)
  --target str          language of output data (default: tr)
  --credentials str     google cloud credentials for translate
                        api (default: credentials.json)
  --save_every int      save batch size (default: 100)
  --logfile str         log file path (default: translator.log)
  --loglevel str        logging level (default: INFO)
  --inline_separator str separator for dialogue-datasets eg.
                        __eou__ (default: None)
```