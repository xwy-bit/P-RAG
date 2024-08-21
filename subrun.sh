IDX=$1
API_KEY=$2
BEGIN=$3
END=$4
for i in $(seq $BEGIN $END)
do
    python -u main.py \
    --engine "gpt-4-0125-preview" \
    --env_idx $i \
    --k 3 \
    --db_path db/train100RA0.db \
    --api_key $API_KEY \
    --log_name "test-$IDX" \
    --dataset "validseen" 
    # --enable_retrieval \
    # --enable_scene_graph
    # --mask_num 50
done
