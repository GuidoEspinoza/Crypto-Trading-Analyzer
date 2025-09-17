# 🔄 Sistema de Migraciones de Base de Datos

Documentación completa del sistema de migraciones para el Crypto Trading Analyzer.

## Descripción General

El sistema de migraciones permite gestionar cambios en la estructura de la base de datos de manera controlada y versionada. Está diseñado para:

- **Evolución segura**: Aplicar cambios de esquema sin pérdida de datos
- **Versionado**: Mantener un historial de cambios en la base de datos
- **Rollback**: Capacidad de revertir cambios si es necesario
- **Automatización**: Aplicación automática de migraciones pendientes

## Arquitectura del Sistema

### Componentes Principales

#### 1. `DatabaseMigration` (Clase Base)

```python
class DatabaseMigration:
    def __init__(self, version: str, description: str)
    def up(self, db_manager: DatabaseManager) -> bool
    def down(self, db_manager: DatabaseManager) -> bool
```

**Propósito**: Clase abstracta que define la estructura de una migración.

**Atributos**:
- `version`: Identificador único de la migración (ej: "001_initial_schema")
- `description`: Descripción legible de los cambios
- `timestamp`: Momento de creación de la migración

**Métodos**:
- `up()`: Aplica los cambios de la migración
- `down()`: Revierte los cambios de la migración

#### 2. `MigrationManager` (Gestor Principal)

```python
class MigrationManager:
    def __init__(self, db_manager: DatabaseManager)
    def register_migration(self, migration: DatabaseMigration)
    def migrate_up(self) -> bool
    def rollback_migration(self, migration: DatabaseMigration) -> bool
```

**Propósito**: Coordina la ejecución de migraciones y mantiene el estado.

**Funcionalidades**:
- Registro de migraciones disponibles
- Tracking de migraciones aplicadas
- Ejecución secuencial de migraciones pendientes
- Rollback de migraciones específicas

### Tabla de Control: `schema_migrations`

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    rollback_sql TEXT
);
```

**Propósito**: Mantiene el registro de qué migraciones han sido aplicadas.

## Migraciones Implementadas

### 1. `InitialSchemaMigration` (001_initial_schema)

**Propósito**: Crear el esquema inicial de la base de datos.

**Operaciones**:
- Crea todas las tablas definidas en `models.py`
- Establece las relaciones y constraints básicos
- Configura los tipos de datos y valores por defecto

**Tablas creadas**:
- `trades`: Registro de operaciones de trading
- `portfolio`: Estado del portfolio
- `strategies`: Configuración y métricas de estrategias
- `backtest_results`: Resultados de backtesting
- `trading_signals`: Señales generadas por estrategias

### 2. `AddIndexesMigration` (002_add_indexes)

**Propósito**: Optimizar el rendimiento mediante índices estratégicos.

**Índices creados**:

#### Tabla `trades`:
- `idx_trades_symbol_status`: Optimiza consultas por símbolo y estado
- `idx_trades_entry_time`: Acelera consultas temporales
- `idx_trades_strategy_symbol`: Mejora filtros por estrategia y símbolo

#### Tabla `portfolio`:
- `idx_portfolio_symbol_paper`: Optimiza consultas de portfolio por tipo

#### Tabla `trading_signals`:
- `idx_signals_symbol_time`: Acelera búsquedas por símbolo y tiempo
- `idx_signals_strategy_type`: Mejora filtros por estrategia y tipo de señal

## Uso del Sistema

### Configuración Inicial

```python
from src.database.migrations import setup_database_migrations, run_migrations
from src.database.database import DatabaseManager

# Crear instancia del database manager
db_manager = DatabaseManager()

# Configurar migraciones
migration_manager = setup_database_migrations(db_manager)

# Ejecutar migraciones pendientes
success = migration_manager.migrate_up()
```

### Ejecución Automática

```python
# Ejecutar todas las migraciones pendientes
success = run_migrations()

# Obtener estado actual
status = get_migration_status()
print(f"Migraciones aplicadas: {status['applied_count']}")
print(f"Migraciones pendientes: {status['pending_count']}")
```

### Verificación de Estado

```python
# Obtener información detallada del estado
status = migration_manager.get_migration_status()

# Estructura del estado:
{
    "total_migrations": 2,
    "applied_count": 2,
    "pending_count": 0,
    "applied_versions": ["001_initial_schema", "002_add_indexes"],
    "pending_versions": [],
    "last_applied": "002_add_indexes"
}
```

## Creación de Nuevas Migraciones

### Paso 1: Definir la Migración

```python
class AddNewFeatureMigration(DatabaseMigration):
    def __init__(self):
        super().__init__("003_add_new_feature", "Add new feature to database")
    
    def up(self, db_manager: DatabaseManager) -> bool:
        try:
            with db_manager.get_db_session() as session:
                # Aplicar cambios
                session.execute(text("""
                    ALTER TABLE trades 
                    ADD COLUMN new_field VARCHAR(50)
                """))
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error in migration: {e}")
            return False
    
    def down(self, db_manager: DatabaseManager) -> bool:
        try:
            with db_manager.get_db_session() as session:
                # Revertir cambios
                session.execute(text("""
                    ALTER TABLE trades 
                    DROP COLUMN new_field
                """))
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error in rollback: {e}")
            return False
```

### Paso 2: Registrar la Migración

```python
def setup_database_migrations(db_manager: DatabaseManager) -> MigrationManager:
    migration_manager = MigrationManager(db_manager)
    
    # Registrar migraciones existentes
    migration_manager.register_migration(InitialSchemaMigration())
    migration_manager.register_migration(AddIndexesMigration())
    
    # Registrar nueva migración
    migration_manager.register_migration(AddNewFeatureMigration())
    
    return migration_manager
```

## Mejores Prácticas

### 1. Nomenclatura de Versiones
- Usar formato: `XXX_descriptive_name`
- Números secuenciales con padding: `001`, `002`, `003`
- Nombres descriptivos y concisos

### 2. Diseño de Migraciones
- **Atomicidad**: Cada migración debe ser una unidad completa
- **Idempotencia**: Poder ejecutar múltiples veces sin efectos adversos
- **Reversibilidad**: Siempre implementar el método `down()`
- **Testing**: Probar tanto `up()` como `down()` antes de desplegar

### 3. Manejo de Datos
- **Preservación**: Nunca eliminar datos sin backup
- **Transformación**: Migrar datos existentes cuando sea necesario
- **Validación**: Verificar integridad después de cambios

### 4. Rollback Strategy
- Implementar rollbacks completos y funcionales
- Documentar dependencias entre migraciones
- Probar rollbacks en entorno de desarrollo

## Logging y Monitoreo

El sistema incluye logging detallado:

```python
# Logs de aplicación
logger.info(f"🔄 Applying migration: {migration.version}")
logger.info(f"✅ Migration {migration.version} applied successfully")

# Logs de error
logger.error(f"❌ Migration {migration.version} failed")
logger.error(f"❌ Error applying migration {migration.version}: {e}")

# Logs de rollback
logger.info(f"⏪ Rolling back migration: {migration.version}")
logger.info(f"✅ Migration {migration.version} rolled back successfully")
```

## Integración con CLI

El sistema se integra con el CLI de gestión de base de datos:

```bash
# Ejecutar migraciones
python src/database/db_manager_cli.py migrate

# Ver estado de migraciones
python src/database/db_manager_cli.py stats
```

## Consideraciones de Seguridad

1. **Backups**: Siempre crear backup antes de migraciones destructivas
2. **Testing**: Probar migraciones en entorno de desarrollo
3. **Rollback Plan**: Tener plan de rollback para cada migración
4. **Monitoring**: Monitorear el proceso de migración en producción

## Troubleshooting

### Problemas Comunes

#### Migración Fallida
```python
# Verificar estado
status = get_migration_status()
print(status['pending_versions'])

# Revisar logs para identificar el error
# Corregir la migración y volver a ejecutar
```

#### Rollback Necesario
```python
# Rollback de migración específica
migration = AddIndexesMigration()
success = migration_manager.rollback_migration(migration)
```

#### Inconsistencia de Estado
```python
# Verificar tabla de migraciones
with db_manager.get_db_session() as session:
    result = session.execute(text(
        "SELECT * FROM schema_migrations ORDER BY applied_at"
    ))
    for row in result:
        print(f"{row.version}: {row.applied_at}")
```

## Próximos Pasos

1. **Migraciones Automáticas**: Integrar con CI/CD
2. **Validación de Esquema**: Verificar integridad post-migración
3. **Migraciones de Datos**: Sistema para transformaciones complejas
4. **Rollback Automático**: Rollback automático en caso de fallo
5. **Métricas**: Tracking de tiempo de ejecución y éxito de migraciones

---

*Este sistema de migraciones proporciona una base sólida para la evolución controlada de la base de datos, garantizando la integridad de los datos y la capacidad de rollback en caso de problemas.*