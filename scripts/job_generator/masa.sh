#! /bin/sh
RANDOM_NUMBER=$$ # Gerando um número aleatório
UPPER_LIMIT=$((100+1)) # Definindo um limite superior para o número gerado
JOB_ID=$(($RANDOM_NUMBER%$UPPER_LIMIT)) # Definindo o JOB_ID
JOB_NAME="Masa-OpenMP Job" # Definindo o JOB_NAME
MASA_INPUT_SEQUENCES_CSV_FILE="masa_input_sequences.csv" # Arquivo CSV que contém as sequências de DNA a serem analisadas nos Jobs
INPUT_SEQUENCES_COUNT=$(wc -l < "$MASA_INPUT_SEQUENCES_CSV_FILE") # Quantidade de Jobs a serem processados
JOB_JSON_FILE="masa_job.json" # Definindo o arquivo de saída JOB_JSON
JOB_COUNTER=0 # Contador de Jobs
CSV_JOB_LIST='' # Lista de Jobs encontrados no CSV e adicionados ao JSON
FASTA_FILES_PATH='fasta/' # Caminho para o diretório que contém as sequências de DNA (.fasta)
EXECUTION_OUTPUT_PATH='' # Caminho de armazenamento para a saída obtida após a execução da aplicação
MEMORY_BOUND='10.060959' # Estimativa de tempo de uso de Memória
IO_BOUND='0.0' # Estimativa de tempo de uso de I/O
while IFS=, read -r primeira_sequencia segunda_sequencia # Fazendo a leitura do arquivo CSV linha por linha e armazenando o nome dos arquivos de seqûencia de dna a serem comparados nas variáveis primeira_sequencia e segunda_sequencia
do
   JOB='    "'$JOB_COUNTER'": {
            "memory": '$MEMORY_BOUND',
            "io": '$IO_BOUND',
            "command": "sh exec.sh '$FASTA_FILES_PATH''$primeira_sequencia' '$FASTA_FILES_PATH''$segunda_sequencia' '$EXECUTION_OUTPUT_PATH'output_'$JOB_COUNTER'.txt",
            "runtime": {
                "c4.large": 6.84,
                "c4.xlarge": 6.84
            }
        },
'
   CSV_JOB_LIST="${CSV_JOB_LIST} $JOB"
   JOB_COUNTER=$(($JOB_COUNTER + 1))
done < $MASA_INPUT_SEQUENCES_CSV_FILE
CSV_JOB_LIST="${CSV_JOB_LIST}    }" # "Fechando lista de Jobs"
cat <<EOF > $JOB_JSON_FILE
{
    "job_id": $JOB_ID,
    "job_name": "$JOB_NAME",
    "description": "A job with $INPUT_SEQUENCES_COUNT task(s) of the Masa-OpenMP application",
    "tasks": {
$CSV_JOB_LIST
}
EOF
