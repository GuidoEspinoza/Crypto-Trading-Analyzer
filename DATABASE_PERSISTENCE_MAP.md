# 🗄️ Mapeo de Persistencia: Órdenes Activas en Base de Datos

## 📋 Objetivo

Implementar persistencia completa de órdenes activas, OCO y posiciones de trading para:
- ✅ **Recuperar estado** después de reinicios del bot
- ✅ **Tracking histórico** de todas las operaciones
- ✅ **Auditoría completa** de órdenes y cancelaciones
- ✅ **Sincronización** entre memoria y base de datos

## 🏗️ Nuevos Modelos de Base de Datos

### 1. **ActiveOrder** - Órdenes Individuales Activas

```python
class ActiveOrder(Base):
    """🎯 Modelo para órdenes individuales activas"""
    __tablename__ = "active_orders"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Binance Order Information
    order_id = Column(BigInteger, nullable=False, index=True)  # Binance order ID
    client_order_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # Order Details
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # BUY, SELL
    order_type = Column(String(20), nullable=False)  # MARKET, LIMIT, STOP_LOSS_LIMIT, etc.
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)  # NULL para MARKET orders
    stop_price = Column(Float, nullable=True)  # Para STOP orders
    
    # Status and State
    status = Column(String(20), nullable=False, default="NEW")  # NEW, FILLED, CANCELLED, etc.
    time_in_force = Column(String(10), nullable=True)  # GTC, IOC, FOK
    
    # Relationships
    position_id = Column(String(50), nullable=True, index=True)  # FK to trading positions
    oco_order_id = Column(Integer, nullable=True, index=True)  # FK to oco_orders
    
    # Trading Context
    is_paper_trade = Column(Boolean, default=True)
    strategy_name = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    binance_time = Column(BigInteger, nullable=True)  # Binance timestamp
    
    def __repr__(self):
        return f"<ActiveOrder(id={self.order_id}, symbol={self.symbol}, type={self.order_type})>"
```

### 2. **ActiveOCOOrder** - Órdenes OCO Activas

```python
class ActiveOCOOrder(Base):
    """🎯 Modelo para órdenes OCO activas"""
    __tablename__ = "active_oco_orders"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Binance OCO Information
    order_list_id = Column(BigInteger, nullable=False, unique=True, index=True)
    list_client_order_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # Order Details
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # BUY, SELL
    quantity = Column(Float, nullable=False)
    
    # Take Profit Order
    tp_order_id = Column(BigInteger, nullable=False)
    tp_client_order_id = Column(String(50), nullable=False)
    tp_price = Column(Float, nullable=False)
    
    # Stop Loss Order
    sl_order_id = Column(BigInteger, nullable=False)
    sl_client_order_id = Column(String(50), nullable=False)
    sl_stop_price = Column(Float, nullable=False)
    sl_limit_price = Column(Float, nullable=True)
    
    # Status and State
    status = Column(String(20), nullable=False, default="EXECUTING")
    list_status_type = Column(String(20), nullable=True)  # OCO, ALL_DONE, REJECT
    list_order_status = Column(String(20), nullable=True)  # EXECUTING, ALL_DONE, REJECT
    
    # Relationships
    position_id = Column(String(50), nullable=True, index=True)  # FK to trading positions
    
    # Trading Context
    is_paper_trade = Column(Boolean, default=True)
    strategy_name = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    binance_time = Column(BigInteger, nullable=True)
    
    def __repr__(self):
        return f"<ActiveOCOOrder(list_id={self.order_list_id}, symbol={self.symbol})>"
```

### 3. **TradingPosition** - Posiciones de Trading Activas

```python
class TradingPosition(Base):
    """📊 Modelo para posiciones de trading activas"""
    __tablename__ = "trading_positions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Position Identification
    position_id = Column(String(50), nullable=False, unique=True, index=True)  # UUID generado
    
    # Position Details
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # BUY, SELL
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    
    # Entry Order Information
    entry_order_id = Column(BigInteger, nullable=False)
    entry_client_order_id = Column(String(50), nullable=False)
    
    # OCO Information (Current)
    current_oco_id = Column(Integer, nullable=True, index=True)  # FK to active_oco_orders
    
    # Position Metrics
    unrealized_pnl = Column(Float, nullable=True)
    unrealized_pnl_pct = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    
    # Risk Management
    initial_tp_price = Column(Float, nullable=True)
    initial_sl_price = Column(Float, nullable=True)
    current_tp_price = Column(Float, nullable=True)
    current_sl_price = Column(Float, nullable=True)
    adjustment_count = Column(Integer, default=0)
    
    # Status and State
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, CLOSED, CANCELLED
    
    # Trading Context
    is_paper_trade = Column(Boolean, default=True)
    strategy_name = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<TradingPosition(id={self.position_id}, symbol={self.symbol}, status={self.status})>"
```

### 4. **OrderHistory** - Historial de Órdenes

```python
class OrderHistory(Base):
    """📜 Modelo para historial completo de órdenes"""
    __tablename__ = "order_history"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Order Information
    order_id = Column(BigInteger, nullable=False, index=True)
    client_order_id = Column(String(50), nullable=False, index=True)
    
    # Order Details
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)
    order_type = Column(String(20), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)
    
    # Execution Details
    executed_qty = Column(Float, nullable=True)
    executed_price = Column(Float, nullable=True)
    commission = Column(Float, nullable=True)
    commission_asset = Column(String(10), nullable=True)
    
    # Status and State
    status = Column(String(20), nullable=False)  # FILLED, CANCELLED, EXPIRED, etc.
    time_in_force = Column(String(10), nullable=True)
    
    # Action Type
    action = Column(String(20), nullable=False)  # CREATED, CANCELLED, FILLED, ADJUSTED
    
    # Relationships
    position_id = Column(String(50), nullable=True, index=True)
    oco_order_id = Column(Integer, nullable=True, index=True)
    
    # Trading Context
    is_paper_trade = Column(Boolean, default=True)
    strategy_name = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    binance_time = Column(BigInteger, nullable=True)
    
    def __repr__(self):
        return f"<OrderHistory(id={self.order_id}, action={self.action}, status={self.status})>"
```

## 🔄 Métodos de Persistencia en BinanceConnector

### 1. **Métodos de Sincronización**

```python
def sync_to_database(self):
    """💾 Sincronizar estado en memoria con base de datos"""
    
def load_from_database(self):
    """📥 Cargar estado desde base de datos al inicializar"""
    
def _save_active_order(self, active_order: ActiveOrder):
    """💾 Guardar orden activa en BD"""
    
def _save_oco_order(self, oco_order: ActiveOCOOrder):
    """💾 Guardar orden OCO en BD"""
    
def _save_trading_position(self, position: TradingPosition):
    """💾 Guardar posición de trading en BD"""
    
def _update_order_status(self, order_id: int, new_status: str):
    """🔄 Actualizar estado de orden en BD"""
```

### 2. **Métodos de Recuperación**

```python
def get_active_orders_from_db(self) -> List[ActiveOrder]:
    """📥 Obtener órdenes activas desde BD"""
    
def get_active_oco_orders_from_db(self) -> List[ActiveOCOOrder]:
    """📥 Obtener órdenes OCO activas desde BD"""
    
def get_trading_positions_from_db(self) -> List[TradingPosition]:
    """📥 Obtener posiciones activas desde BD"""
    
def restore_state_from_database(self):
    """🔄 Restaurar estado completo desde BD"""
```

### 3. **Métodos de Limpieza**

```python
def cleanup_completed_orders(self):
    """🧹 Limpiar órdenes completadas de memoria y BD"""
    
def archive_closed_positions(self):
    """📦 Archivar posiciones cerradas"""
    
def _move_to_history(self, order_id: int, action: str):
    """📜 Mover orden a historial"""
```

## 🔧 Modificaciones en BinanceConnector

### A. **Constructor `__init__`**

```python
def __init__(self, config=None, auto_restore=True):
    # ... código existente ...
    
    # Database session
    self.db_session = None
    
    # Auto-restore state from database
    if auto_restore:
        self.restore_state_from_database()
```

### B. **Método `create_oco_order`**

```python
def create_oco_order(self, ...):
    # ... lógica existente ...
    
    if result.success:
        # Guardar en memoria (existente)
        self.active_oco_orders[oco_order.order_list_id] = oco_order
        
        # NUEVO: Guardar en base de datos
        self._save_oco_order(oco_order)
        
        # NUEVO: Guardar órdenes individuales
        self._save_active_order(tp_order)
        self._save_active_order(sl_order)
```

### C. **Método `cancel_oco_order`**

```python
def cancel_oco_order(self, order_list_id: int):
    # ... lógica existente ...
    
    if cancel_result.success:
        # Remover de memoria (existente)
        del self.active_oco_orders[order_list_id]
        
        # NUEVO: Actualizar estado en BD
        self._update_oco_status(order_list_id, "CANCELLED")
        
        # NUEVO: Mover a historial
        self._move_oco_to_history(order_list_id, "CANCELLED")
```

### D. **Método `create_trading_position`**

```python
def create_trading_position(self, ...):
    # ... lógica existente ...
    
    if position_created:
        # Guardar en memoria (existente)
        self.trading_positions[position.position_id] = position
        
        # NUEVO: Guardar en base de datos
        self._save_trading_position(position)
```

## 📊 Migración de Base de Datos

### **Nueva Migración: `add_order_persistence_tables.py`**

```python
class AddOrderPersistenceTablesMigration(DatabaseMigration):
    def __init__(self):
        super().__init__(
            version="20240115_001",
            description="Add tables for order persistence and tracking"
        )
    
    def up(self, session):
        """Crear tablas de persistencia de órdenes"""
        # Crear todas las nuevas tablas
        Base.metadata.create_all(bind=session.bind, tables=[
            ActiveOrder.__table__,
            ActiveOCOOrder.__table__,
            TradingPosition.__table__,
            OrderHistory.__table__
        ])
    
    def down(self, session):
        """Eliminar tablas de persistencia de órdenes"""
        # Drop tables in reverse order
        session.execute(text("DROP TABLE IF EXISTS order_history"))
        session.execute(text("DROP TABLE IF EXISTS trading_positions"))
        session.execute(text("DROP TABLE IF EXISTS active_oco_orders"))
        session.execute(text("DROP TABLE IF EXISTS active_orders"))
```

## 🎯 Flujo de Persistencia Completo

### **Escenario 1: Crear Posición Nueva**
```
1. BinanceConnector.create_trading_position()
2. ├── Crear entrada MARKET
3. ├── Crear OCO (TP + SL)
4. ├── Guardar en memoria (existente)
5. └── NUEVO: Guardar en BD
    ├── INSERT INTO trading_positions
    ├── INSERT INTO active_oco_orders
    └── INSERT INTO active_orders (TP + SL)
```

### **Escenario 2: Ajustar TP/SL**
```
1. BinanceConnector.adjust_oco_levels()
2. ├── Cancelar OCO existente
3. ├── Crear nuevo OCO
4. ├── Actualizar memoria (existente)
5. └── NUEVO: Actualizar BD
    ├── UPDATE active_oco_orders SET status='CANCELLED'
    ├── INSERT INTO order_history (cancelación)
    ├── INSERT INTO active_oco_orders (nuevo OCO)
    └── UPDATE trading_positions SET adjustment_count++
```

### **Escenario 3: Reinicio del Bot**
```
1. BinanceConnector.__init__(auto_restore=True)
2. └── restore_state_from_database()
    ├── SELECT * FROM active_orders WHERE status='NEW'
    ├── SELECT * FROM active_oco_orders WHERE status='EXECUTING'
    ├── SELECT * FROM trading_positions WHERE status='ACTIVE'
    └── Reconstruir diccionarios en memoria
```

### **Escenario 4: Reset con Profit**
```
1. BinanceConnector.close_position_with_profit()
2. ├── Cancelar OCO pendiente
3. ├── Ejecutar MARKET de cierre
4. ├── Actualizar memoria (existente)
5. └── NUEVO: Actualizar BD
    ├── UPDATE trading_positions SET status='CLOSED', closed_at=NOW()
    ├── UPDATE active_oco_orders SET status='CANCELLED'
    └── INSERT INTO order_history (cierre)
```

## ✅ Checklist de Implementación

### 🔄 Modelos de Base de Datos
- [ ] Crear modelo `ActiveOrder`
- [ ] Crear modelo `ActiveOCOOrder`
- [ ] Crear modelo `TradingPosition`
- [ ] Crear modelo `OrderHistory`

### 🔄 Migración de BD
- [ ] Crear migración para nuevas tablas
- [ ] Implementar métodos `up()` y `down()`
- [ ] Registrar migración en sistema

### 🔄 Métodos de Persistencia
- [ ] Implementar `_save_active_order()`
- [ ] Implementar `_save_oco_order()`
- [ ] Implementar `_save_trading_position()`
- [ ] Implementar `_update_order_status()`

### 🔄 Métodos de Recuperación
- [ ] Implementar `restore_state_from_database()`
- [ ] Implementar `get_active_orders_from_db()`
- [ ] Implementar `get_active_oco_orders_from_db()`
- [ ] Implementar `get_trading_positions_from_db()`

### 🔄 Integración con Métodos Existentes
- [ ] Modificar `create_oco_order()` para persistir
- [ ] Modificar `cancel_oco_order()` para actualizar BD
- [ ] Modificar `create_trading_position()` para persistir
- [ ] Modificar `close_position_with_profit()` para actualizar BD

### 🔄 Métodos de Limpieza
- [ ] Implementar `cleanup_completed_orders()`
- [ ] Implementar `archive_closed_positions()`
- [ ] Implementar `_move_to_history()`

### 🔄 Testing y Validación
- [ ] Tests unitarios para nuevos modelos
- [ ] Tests de integración para persistencia
- [ ] Tests de recuperación de estado
- [ ] Validación de sincronización memoria-BD

## 🎯 Resultado Final

Una vez implementada la persistencia completa:

✅ **Estado persistente** - El bot mantiene estado entre reinicios
✅ **Auditoría completa** - Historial de todas las órdenes y cambios
✅ **Recuperación robusta** - Restauración automática del estado
✅ **Sincronización** - Memoria y BD siempre sincronizadas
✅ **Limpieza automática** - Archivado de órdenes completadas
✅ **Tracking histórico** - Análisis de performance y debugging

## 🚀 Próximos Pasos

1. **Implementar modelos** de BD según especificación
2. **Crear migración** para nuevas tablas
3. **Implementar métodos** de persistencia en BinanceConnector
4. **Actualizar métodos existentes** para usar persistencia
5. **Testing exhaustivo** de recuperación de estado
6. **Documentar configuración** de base de datos