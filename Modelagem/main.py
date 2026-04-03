from utils import gerar_clientes, get_bcb_series
import matplotlib.pyplot as plt
import seaborn as sns

def main():

    df = get_bcb_series('15940')
    print(df.head(20))
    # clientes = gerar_clientes()
    # print(clientes.head(20))

    # plt.hist(clientes["score_credito"], bins=100)
    # plt.show()

    # plt.figure(figsize=(10,6))
    # sns.heatmap(clientes.corr(numeric_only=True), annot=True, cmap='coolwarm')
    # plt.title('Matriz de Correlação')
    # plt.show()

if __name__ == "__main__":
    main()