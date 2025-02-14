# NNLangID :earth_americas::speech_balloon:
Project for neural network-based tweet language identification. See [project report](TweetLanguageIdentification_D.Sauter-A.Heilig-T.Kiupel_rev1.pdf) for more details.

## Terminal Screenshot
![](TerminalManual.PNG "Classified manually entered text.")

## Architecture Overview
![](ArchitectureOverview.png "Simplified overview of the general architecture.")

## Getting Started
* Fetch tweet data from Twitter via the `TweetRetriever.py` and place it into `data/input_data/original` (already done for the [Twitter blog post](https://blog.twitter.com/engineering/en_us/a/2015/evaluating-language-identification-performance.html) data this project is based on).
* Run `Main.py` for the main procedure. Depending on `use_cluster_params` it reads in one of the two YAML settings files, which contain all user parameters.
	* Set **`create_splitted_data_files = True`** to split an original file from specified file path `input_tr_va_te_data_rel_path` into separate training, validation and test set files. The data is then fetched from those files, preprocessed and transformed to be readily used by the subsequent embedding and RNN.
	* Set **`train_embed = True`** to train the embedding and get the embedding weights. The embedding is implemented as a Skip-Gram model with Negative Sampling. While training, the loss-based best embedding model checkpoint and extracted embedding weights are automatically saved to specified file paths in `embed_model_checkpoint_rel_path` and `embed_weights_rel_path`.
	* Set **`train_rnn = True`** to use the embedding weights to embed the characters of a tweet and feed them into the RNN, which is implemented as a (uni- or bidirectional) GRU model. While training, the loss-based best RNN model checkpoint is automatically saved to the specified file path in `rnn_model_checkpoint_rel_path`.
	* Set **`eval_test_set = True`** to evaluate a trained RNN model checkpoint on the test set, to get further metrics on the performance, which are then stored back to the checkpoint file. (File paths specified in `rnn_model_checkpoint_rel_path` and `embed_weights_rel_path` are used).
	* Set **`run_terminal = True`** to run the terminal for interactive evaluation of a trained RNN model checkpoint with arbitrary input text or live tweets fetched directly from Twitter. Some trained model checkpoints and weight files may be found in `data/save/trained`. (File paths specified in `trained_model_checkpoint_rel_path` and `trained_embed_weights_rel_path` are used.)
	* Set **`print_embed_testing = True`** to print the embedding test after the embedding calculation to the console.
	* Set **`print_model_checkpoint_embed_weights`** and **`print_rnn_model_checkpoint`** or **`print_embed_model_checkpoint`** to the respective file paths to print stored model checkpoint data to the console. (Note: Some parameters in the YAML settings file, e.g. `input_tr_va_te_data_rel_path` and `hidden_size_rnn`, have to be the same as in the model checkpoint file!)

### Prerequisites
* Python v2.7
* PyTorch v0.2.0_4
* CUDA is used if available.

## Authors
Project developed by Alexander Heilig, Dominik Sauter and Tabea Kiupel in the context of the Neural Networks practical course at the Karlsruhe Institute of Technology (KIT), Germany.

## License
Licensed unter the MIT license (see [LICENSE](LICENSE) file for more details).