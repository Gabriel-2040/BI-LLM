from sqlalchemy import create_engine, text

def test_postgres15():
    print("🔍 Testando conexão com PostgreSQL 15 (porta 5432)...")
    
    # Tentativa sem senha
    connection_string = "postgresql://postgres@localhost:5432/bi_dw"
    
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            # Teste básico
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conexão bem-sucedida!")
            print(f"📊 {version}")
            
            # Verificar se o banco bi_dw existe e está vazio
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            print(f"📋 Tabelas no banco 'bi_dw': {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
                
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        
        # Tentativa com informações mais detalhadas
        print("\n🔧 Diagnosticando o problema...")
        print("1. Verifique se o PostgreSQL 15 está rodando")
        print("2. Verifique se o banco 'bi_dw' existe")
        print("3. Tente conectar via pgAdmin no PostgreSQL 15")
        return False

if __name__ == "__main__":
    test_postgres15()