import torch.nn as nn
from fla.layers.hgrn import HGRNAttention

class SmallHGRNLM(nn.Module):
    def __init__(self, vocab_size, hidden_size, num_layers):
        super(SmallHGRNLM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.hgrn = HGRNAttention(num_layers=num_layers, hidden_size=hidden_size)
        self.prediction_head = nn.Linear(hidden_size, vocab_size)

    def forward(self, input_ids, hidden=None):
        embedded = self.embedding(input_ids)
        output, hidden = self.hgrn(embedded, hidden=hidden)
        logits = self.prediction_head(output)
        return logits, hidden

# Пример создания модели
vocab_size = 50000  # Размер словаря, например, для русского языка
hidden_size = 256   # Размер скрытого состояния
num_layers = 2      # Количество слоев
model = SmallHGRNLM(vocab_size=vocab_size, hidden_size=hidden_size, num_layers=num_layers)
model.to('cpu')