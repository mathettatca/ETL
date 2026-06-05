Mình hiểu thay đổi trong phần Summary như này:

`modules/data_access` không phải API service, cũng không phải một service độc lập để expose endpoint. Nó là **application package / shared data access layer** cho các module khác trong project gọi vào. Tức là caller sẽ là các module nội bộ phụ thuộc vào `data_access`, ví dụ data loader / processing / ingestion, chứ không phải HTTP client hay external service.

Flow mới được nhấn mạnh là:

```text
module khác trong project -> data_access mediator -> handler -> repository -> response
```

Điểm khác so với plan cũ: mediator không nên được hiểu như API boundary, mà là **internal application boundary** để chuẩn hóa cách các module truy cập dữ liệu.

**Hướng sửa đổi đề xuất**

1. **Docs / naming**
   - Sửa wording trong docs/code comment từ “request” theo nghĩa API sang “command/query call” hoặc “application request”.
   - Tránh mô tả như external service.
   - `main.py` chỉ nên là example/use case local, không phải entrypoint API.

2. **Mediator interface**
   - Giữ `mediator.send(command_or_query)` là đúng.
   - Không cần async/web framework/http context.
   - Không cần DTO API layer.
   - Không dùng pipeline behavior trong mediator.
   - Caller nội bộ sẽ import command/query rồi gọi mediator.

3. **Package boundary**
   - Nên expose public API gọn ở `modules/data_access/__init__.py` hoặc `modules/data_access/mediator/__init__.py`, ví dụ:
   ```python
   from modules.data_access.mediator import build_data_access_mediator
   from modules.data_access.application.request.commands import AuditGDriveFileCommand
   ```
   để module khác không phải biết sâu vào handler/repository.

4. **Dependency direction**
   - Module khác chỉ gọi:
   ```python
   mediator.send(AuditGDriveFileCommand(...))
   ```
   - Không gọi trực tiếp:
   ```python
   AuditGDriveFileCommandHandler()
   BaseMongoRepository(...)
   ```
   vì như vậy phá centralize data access layer.

5. **Audit behavior**
   - Mediator không còn chịu trách nhiệm audit/logging/error pipeline.
   - Nếu use case cần audit, xử lý trong handler/service riêng và không đặt caller metadata trong `BaseRequest`.

6. **Tests cần bổ sung sau**
   - Test một module giả gọi mediator như consumer nội bộ.
   - Test không cần HTTP/API.
   - Test public import path của package để đảm bảo module khác dùng được ổn định.

Tóm lại: hướng sửa không phải thay đổi lớn về kiến trúc, mà là **làm rõ data_access là internal application package**, mediator là internal dispatcher, và public API của package nên gọn để các module khác gọi vào mà không chạm handler/repository trực tiếp.
