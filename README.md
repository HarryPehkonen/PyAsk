# AI Conversation Assistant

## Project Description

This project is an AI conversation assistant that utilizes a large language model (LLM) to engage in interactive conversations. The assistant can load and save conversations, handle tool calls, and manage extensions dynamically.

## Features

- **Interactive Conversations**: Engage in conversations with an AI powered by a large language model.
- **Conversation Management**: Save and load conversations to/from disk.
- **Tool Integration**: Handle tool calls within the conversation context.
- **Extension Management**: Dynamically import and manage Python modules as extensions.
- **Command-Line Interface**: Interact with the assistant via command-line with support for single-line and multi-line inputs.

## Installation

To install and set up the project, follow these steps:

1. Clone the repository:
```sh
git clone <repository-url>
```
2. Navigate to the project directory:
```sh
cd <project-directory>
```
3. Install the required dependencies:
```sh
pip install sqlite3 langchain-mistralai
```

## Usage

To use the AI conversation assistant, run the following command:
```sh
python ask.py <ai_code_name> [--multiline] [--new]
```
- `<ai_code_name>`: The code name of the AI assistant.  This code name is used to select the "personality", or one of your pre-defined system messages.
- `--multiline`: Enable multi-line input mode.  When you select --multiline, a line with nothing but a period will end the input session, and process the prompt.
- `--new`: Start a new conversation by deleting the existing one.

### Example
```sh
python ask.py betsy --multiline
```

## SQLite Database Tables

The SQLite database tables that can be used are the system_prompts table, table_metadata, and column_metadata tables.  The metadata tables hold information about the contents of the database.  This information will be appended to the system message so your AI will always know what is in the database and where to find it.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch:
```sh
git checkout -b feature/your-feature-name
```
3. Make your changes and commit them:
```sh
git commit -m 'Add your feature'
```
4. Push to the branch:
```sh
git push origin feature/your-feature-name
```
5. Open a pull request.

## License

This project is licensed under the Unlicense. See the [LICENSE](LICENSE) file for more details.
