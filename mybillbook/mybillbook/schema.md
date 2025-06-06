# django_migrations
|  Field  |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id      | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| app     | varchar(255) | NO       |     |         |       |               |
| name    | varchar(255) | NO       |     |         |       |               |
| applied | datetime     | NO       |     |         |       |               |

# django_content_type
|   Field   |     Type     | Nullable | Key | Default | Index |     Extra     |
| --------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id        | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| app_label | varchar(100) | NO       |     |         |   X   |               |
| model     | varchar(100) | NO       |     |         |   X   |               |

# auth_group_permissions
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| group_id      | integer | NO       |     |         |   X   |               |
| permission_id | integer | NO       |     |         |   X   |               |

# auth_permission
|      Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id              | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| content_type_id | integer      | NO       |     |         |   X   |               |
| codename        | varchar(100) | NO       |     |         |   X   |               |
| name            | varchar(255) | NO       |     |         |   X   |               |

# auth_group
| Field |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id    | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| name  | varchar(150) | NO       | UNI |         |   X   |               |

# users_subscriptionplan
|     Field     |    Type     | Nullable | Key | Default | Index |     Extra     |
| ------------- | ----------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer     | NO       | PRI |         |   X   | AUTOINCREMENT |
| name          | varchar(20) | NO       | UNI |         |   X   |               |
| price         | decimal     | NO       |     |         |       |               |
| duration_days | integer     | NO       |     |         |       |               |
| features      | text        | NO       |     |         |       |               |

# users_user
|        Field        |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                  | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| password            | varchar(128) | NO       |     |         |       |               |
| last_login          | datetime     | YES      |     | NULL    |       |               |
| is_superuser        | bool         | NO       |     |         |       |               |
| mobile              | varchar(15)  | NO       | UNI |         |   X   |               |
| is_active           | bool         | NO       |     |         |       |               |
| is_staff            | bool         | NO       |     |         |       |               |
| name                | varchar(100) | YES      |     | NULL    |       |               |
| email               | varchar(254) | YES      |     | NULL    |       |               |
| profile_picture     | varchar(100) | YES      |     | NULL    |       |               |
| current_business_id | bigint       | YES      |     | NULL    |   X   |               |

# users_user_groups
|  Field   |  Type   | Nullable | Key | Default | Index |     Extra     |
| -------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id       | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| user_id  | bigint  | NO       |     |         |   X   |               |
| group_id | integer | NO       |     |         |   X   |               |

# users_user_user_permissions
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| user_id       | bigint  | NO       |     |         |   X   |               |
| permission_id | integer | NO       |     |         |   X   |               |

# users_business
|       Field       |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| name              | varchar(255) | NO       |     |         |       |               |
| phone             | varchar(15)  | NO       |     |         |       |               |
| email             | varchar(254) | YES      |     | NULL    |       |               |
| business_address  | text         | NO       |     |         |       |               |
| street_address    | text         | NO       |     |         |       |               |
| city              | varchar(100) | YES      |     | NULL    |       |               |
| state             | varchar(100) | YES      |     | NULL    |       |               |
| pincode           | varchar(10)  | YES      |     | NULL    |       |               |
| pan_number        | varchar(15)  | YES      |     | NULL    |       |               |
| gstin             | varchar(15)  | YES      |     | NULL    |       |               |
| tds               | bool         | NO       |     |         |       |               |
| tcs               | bool         | NO       |     |         |       |               |
| business_type     | text         | NO       |     |         |       |               |
| industry_type     | varchar(50)  | YES      |     | NULL    |       |               |
| registration_type | varchar(50)  | YES      |     | NULL    |       |               |
| signature         | varchar(100) | YES      |     | NULL    |       |               |
| website           | varchar(200) | YES      |     | NULL    |       |               |
| created_at        | datetime     | NO       |     |         |       |               |
| owner_id          | bigint       | NO       |     |         |   X   |               |

# users_auditlog
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| action      | varchar(255) | NO       |     |         |       |               |
| metadata    | text         | NO       |     |         |       |               |
| created_at  | datetime     | NO       |     |         |       |               |
| user_id     | bigint       | YES      |     | NULL    |   X   |               |
| business_id | bigint       | YES      |     | NULL    |   X   |               |

# users_role
|    Field    |    Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ----------- | -------- | --- | ------- | :---: | ------------- |
| id          | integer     | NO       | PRI |         |   X   | AUTOINCREMENT |
| role_name   | varchar(30) | NO       |     |         |       |               |
| permissions | text        | NO       |     |         |       |               |
| is_removed  | bool        | NO       |     |         |       |               |
| business_id | bigint      | YES      |     | NULL    |   X   |               |
| user_id     | bigint      | YES      |     | NULL    |   X   |               |

# users_staffinvite
|     Field     |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id            | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| mobile        | varchar(15)  | NO       |     |         |       |               |
| name          | varchar(255) | NO       |     |         |       |               |
| role_name     | varchar(30)  | NO       |     |         |       |               |
| status        | varchar(20)  | NO       |     |         |       |               |
| created_at    | datetime     | NO       |     |         |       |               |
| business_id   | bigint       | NO       |     |         |   X   |               |
| invited_by_id | bigint       | YES      |     | NULL    |   X   |               |

# users_subscription
|    Field    |   Type   | Nullable | Key | Default | Index |     Extra     |
| ----------- | -------- | -------- | --- | ------- | :---: | ------------- |
| id          | integer  | NO       | PRI |         |   X   | AUTOINCREMENT |
| start_date  | datetime | NO       |     |         |       |               |
| end_date    | datetime | NO       |     |         |       |               |
| is_active   | bool     | NO       |     |         |       |               |
| business_id | bigint   | NO       | UNI |         |   X   |               |
| plan_id     | bigint   | YES      |     | NULL    |   X   |               |

# django_admin_log
|      Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id              | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| object_id       | text         | YES      |     | NULL    |       |               |
| object_repr     | varchar(200) | NO       |     |         |       |               |
| action_flag     | smallint     | NO       |     |         |       |               |
| change_message  | text         | NO       |     |         |       |               |
| content_type_id | integer      | YES      |     | NULL    |   X   |               |
| user_id         | bigint       | NO       |     |         |   X   |               |
| action_time     | datetime     | NO       |     |         |       |               |

# sales_tcs
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| rate        | decimal      | YES      |     | NULL    |   X   |               |
| section     | varchar(250) | YES      |     | NULL    |   X   |               |
| description | text         | YES      |     | NULL    |   X   |               |
| condition   | text         | YES      |     | NULL    |       |               |
| business_id | bigint       | YES      |     | NULL    |   X   |               |

# sales_tds
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| rate        | decimal      | YES      |     | NULL    |   X   |               |
| section     | varchar(250) | YES      |     | NULL    |   X   |               |
| description | text         | YES      |     | NULL    |   X   |               |
| business_id | bigint       | YES      |     | NULL    |   X   |               |

# inventory_gsttaxrate
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| rate        | decimal      | NO       |     |         |       |               |
| cess_rate   | decimal      | NO       |     |         |       |               |
| description | varchar(255) | NO       |     |         |       |               |

# inventory_measuringunit
| Field |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id    | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| name  | varchar(100) | NO       | UNI |         |   X   |               |

# automated_bills_automatedinvoice
|        Field         |     Type     | Nullable | Key | Default | Index |     Extra     |
| -------------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                   | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| automated_invoice_no | varchar(50)  | NO       | UNI |         |   X   |               |
| start_date           | date         | NO       |     |         |       |               |
| end_date             | date         | NO       |     |         |       |               |
| repeat_every         | integer      | NO       |     |         |       |               |
| repeat_unit          | varchar(10)  | NO       |     |         |       |               |
| payment_terms        | integer      | NO       |     |         |       |               |
| discount             | decimal      | NO       |     |         |       |               |
| apply_tcs            | bool         | NO       |     |         |       |               |
| tcs_amount           | decimal      | NO       |     |         |       |               |
| tcs_on               | varchar(20)  | NO       |     |         |       |               |
| total_amount         | decimal      | NO       |     |         |       |               |
| notes                | text         | YES      |     | NULL    |       |               |
| signature            | varchar(100) | YES      |     | NULL    |       |               |
| status               | varchar(10)  | NO       |     |         |       |               |
| business_id          | bigint       | NO       |     |         |   X   |               |
| party_id             | bigint       | NO       |     |         |   X   |               |
| tcs_id               | bigint       | YES      |     | NULL    |   X   |               |

# automated_bills_automatedinvoiceitem
|        Field        |    Type     | Nullable | Key | Default | Index |     Extra     |
| ------------------- | ----------- | -------- | --- | ------- | :---: | ------------- |
| id                  | integer     | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity            | decimal     | NO       |     |         |       |               |
| discount            | decimal     | NO       |     |         |       |               |
| hsn_code            | varchar(20) | YES      |     | NULL    |       |               |
| price_item          | decimal     | YES      |     | NULL    |       |               |
| unit_price          | decimal     | YES      |     | NULL    |       |               |
| automatedinvoice_id | bigint      | NO       |     |         |   X   |               |
| gstTaxRate_id       | bigint      | YES      |     | NULL    |   X   |               |
| item_id             | bigint      | YES      |     | NULL    |   X   |               |
| service_id          | bigint      | YES      |     | NULL    |   X   |               |

# cash_and_bank_bankaccount
|        Field        |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                  | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| account_name        | varchar(100) | NO       |     |         |       |               |
| account_type        | varchar(10)  | NO       |     |         |       |               |
| opening_balance     | decimal      | NO       |     |         |       |               |
| current_balance     | decimal      | NO       |     |         |       |               |
| as_of_date          | date         | NO       |     |         |       |               |
| bank_account_number | varchar(20)  | YES      |     | NULL    |       |               |
| ifsc_code           | varchar(20)  | YES      |     | NULL    |       |               |
| bank_branch_name    | varchar(100) | YES      |     | NULL    |       |               |
| account_holder_name | varchar(100) | YES      |     | NULL    |       |               |
| upi_id              | varchar(50)  | YES      |     | NULL    |       |               |
| created_at          | datetime     | NO       |     |         |       |               |
| business_id         | bigint       | NO       |     |         |   X   |               |

# cash_and_bank_banktransaction
|       Field        |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------------------ | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                 | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| transaction_type   | varchar(20)  | NO       |     |         |   X   |               |
| amount             | decimal      | NO       |     |         |       |               |
| date               | date         | NO       |     |         |   X   |               |
| reference          | varchar(100) | YES      |     | NULL    |       |               |
| notes              | text         | YES      |     | NULL    |       |               |
| created_at         | datetime     | NO       |     |         |       |               |
| updated_at         | datetime     | NO       |     |         |       |               |
| account_id         | bigint       | NO       |     |         |   X   |               |
| business_id        | bigint       | NO       |     |         |   X   |               |
| credit_note_id     | bigint       | YES      |     | NULL    |   X   |               |
| debit_note_id      | bigint       | YES      |     | NULL    |   X   |               |
| invoice_id         | bigint       | YES      |     | NULL    |   X   |               |
| payment_in_id      | bigint       | YES      |     | NULL    |   X   |               |
| payment_out_id     | bigint       | YES      |     | NULL    |   X   |               |
| purchase_id        | bigint       | YES      |     | NULL    |   X   |               |
| purchase_return_id | bigint       | YES      |     | NULL    |   X   |               |
| sales_return_id    | bigint       | YES      |     | NULL    |   X   |               |

# einvoicing_gstr1reconciliation
|        Field        |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                  | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| gst_invoice_no      | varchar(100) | YES      |     | NULL    |       |               |
| gst_invoice_date    | date         | YES      |     | NULL    |       |               |
| gst_invoice_value   | decimal      | YES      |     | NULL    |       |               |
| gst_gstin           | varchar(15)  | YES      |     | NULL    |       |               |
| local_invoice_value | decimal      | YES      |     | NULL    |       |               |
| local_gstin         | varchar(15)  | YES      |     | NULL    |       |               |
| status              | varchar(50)  | NO       |     |         |       |               |
| remarks             | text         | YES      |     | NULL    |       |               |
| created_at          | datetime     | NO       |     |         |       |               |
| updated_at          | datetime     | NO       |     |         |       |               |
| invoice_id          | bigint       | YES      |     | NULL    |   X   |               |

# einvoicing_einvoice
|     Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| -------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id             | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| status         | varchar(20)  | NO       |     |         |       |               |
| irn            | varchar(100) | YES      | UNI | NULL    |   X   |               |
| raw_invoice    | text         | YES      |     | NULL    |       |               |
| ack_no         | varchar(50)  | YES      |     | NULL    |       |               |
| ack_date       | datetime     | YES      |     | NULL    |       |               |
| signed_invoice | text         | YES      |     | NULL    |       |               |
| signed_qr_code | text         | YES      |     | NULL    |       |               |
| qr_code_image  | varchar(100) | YES      |     | NULL    |       |               |
| invoice_type   | varchar(20)  | NO       |     |         |       |               |
| supply_type    | varchar(20)  | NO       |     |         |       |               |
| document_type  | varchar(20)  | NO       |     |         |       |               |
| seller_gstin   | varchar(15)  | NO       |     |         |       |               |
| buyer_gstin    | varchar(15)  | NO       |     |         |       |               |
| error_message  | text         | YES      |     | NULL    |       |               |
| created_at     | datetime     | NO       |     |         |       |               |
| updated_at     | datetime     | NO       |     |         |       |               |
| invoice_id     | bigint       | NO       | UNI |         |   X   |               |

# einvoicing_ewaybill
|      Field       |     Type     | Nullable | Key | Default | Index |     Extra     |
| ---------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id               | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| status           | varchar(30)  | NO       |     |         |       |               |
| irn              | varchar(64)  | NO       | UNI |         |   X   |               |
| trans_id         | varchar(15)  | NO       |     |         |       |               |
| trans_name       | varchar(100) | NO       |     |         |       |               |
| trans_mode       | varchar(1)   | NO       |     |         |       |               |
| distance         | integer      | NO       |     |         |       |               |
| trans_doc_no     | varchar(15)  | NO       |     |         |       |               |
| trans_doc_dt     | varchar(10)  | NO       |     |         |       |               |
| veh_no           | varchar(20)  | NO       |     |         |       |               |
| veh_type         | varchar(1)   | NO       |     |         |       |               |
| exp_ship_addr1   | varchar(100) | NO       |     |         |       |               |
| exp_ship_addr2   | varchar(100) | YES      |     | NULL    |       |               |
| exp_ship_loc     | varchar(100) | NO       |     |         |       |               |
| exp_ship_pin     | integer      | NO       |     |         |       |               |
| exp_ship_stcd    | varchar(2)   | NO       |     |         |       |               |
| disp_name        | varchar(100) | NO       |     |         |       |               |
| disp_addr1       | varchar(100) | NO       |     |         |       |               |
| disp_addr2       | varchar(100) | YES      |     | NULL    |       |               |
| disp_loc         | varchar(100) | NO       |     |         |       |               |
| disp_pin         | integer      | NO       |     |         |       |               |
| disp_stcd        | varchar(2)   | NO       |     |         |       |               |
| generated_date   | datetime     | YES      |     | NULL    |       |               |
| valid_upto       | datetime     | YES      |     | NULL    |       |               |
| request_payload  | text         | YES      |     | NULL    |       |               |
| response_payload | text         | YES      |     | NULL    |       |               |
| is_cancelled     | bool         | NO       |     |         |       |               |
| cancel_reason    | text         | YES      |     | NULL    |       |               |
| created_at       | datetime     | NO       |     |         |       |               |
| updated_at       | datetime     | NO       |     |         |       |               |
| invoice_id       | bigint       | NO       | UNI |         |   X   |               |

# expenses_expensecategory
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| name        | varchar(100) | NO       |     |         |   X   |               |
| created_at  | date         | NO       |     |         |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# expenses_expense
|        Field        |    Type     | Nullable | Key | Default | Index |     Extra     |
| ------------------- | ----------- | -------- | --- | ------- | :---: | ------------- |
| id                  | integer     | NO       | PRI |         |   X   | AUTOINCREMENT |
| expense_no          | varchar(50) | NO       |     |         |   X   |               |
| original_invoice_no | varchar(50) | YES      |     | NULL    |       |               |
| date                | date        | NO       |     |         |       |               |
| expense_with_gst    | bool        | NO       |     |         |       |               |
| payment_method      | varchar(20) | YES      |     | NULL    |       |               |
| notes               | text        | YES      |     | NULL    |       |               |
| discount            | decimal     | NO       |     |         |       |               |
| total_amount        | decimal     | NO       |     |         |       |               |
| taxable_amount      | decimal     | NO       |     |         |       |               |
| business_id         | bigint      | YES      |     | NULL    |   X   |               |
| party_id            | bigint      | YES      |     | NULL    |   X   |               |
| category_id         | bigint      | NO       |     |         |   X   |               |

# expenses_expenseitem
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity      | decimal | NO       |     |         |       |               |
| discount      | decimal | NO       |     |         |       |               |
| unit_price    | decimal | YES      |     | NULL    |       |               |
| amount        | decimal | YES      |     | NULL    |       |               |
| expense_id    | bigint  | NO       |     |         |   X   |               |
| gstTaxRate_id | bigint  | YES      |     | NULL    |   X   |               |
| service_id    | bigint  | YES      |     | NULL    |   X   |               |
| item_id       | bigint  | YES      |     | NULL    |   X   |               |

# expenses_expenseservice
|       Field       |              Type               | Nullable | Key | Default | Index |     Extra     |
| ----------------- | ------------------------------- | -------- | --- | ------- | :---: | ------------- |
| id                | integer                         | NO       | PRI |         |   X   | AUTOINCREMENT |
| serviceName       | varchar(255)                    | NO       |     |         |       |               |
| serviceType       | varchar(10)                     | NO       |     |         |       |               |
| purchasePrice     | decimal                         | NO       |     |         |       |               |
| purchasePriceType | varchar(50)                     | NO       |     |         |       |               |
| ITC               | varchar(50)                     | NO       |     |         |       |               |
| sacCode           | varchar(15)                     | YES      |     | NULL    |       |               |
| business_id       | bigint                          | NO       |     |         |   X   |               |
| gstTaxRate_id     | bigint                          | YES      |     | NULL    |   X   |               |
| measuringUnit_id  | bigint                          | YES      |     | NULL    |   X   |               |
| CONSTRAINT        | unique_serviceName_per_business | YES      | UNI | NULL    |   X   |               |
| serviceName       | )                               | YES      |     | NULL    |       |               |

# expenses_item
|       Field       |             Type             | Nullable | Key | Default | Index |     Extra     |
| ----------------- | ---------------------------- | -------- | --- | ------- | :---: | ------------- |
| id                | integer                      | NO       | PRI |         |   X   | AUTOINCREMENT |
| itemName          | varchar(255)                 | NO       |     |         |       |               |
| itemType          | varchar(10)                  | NO       |     |         |       |               |
| purchasePrice     | decimal                      | NO       |     |         |       |               |
| purchasePriceType | varchar(50)                  | NO       |     |         |       |               |
| ITC               | varchar(50)                  | NO       |     |         |       |               |
| hsnCode           | varchar(15)                  | YES      |     | NULL    |       |               |
| business_id       | bigint                       | NO       |     |         |   X   |               |
| gstTaxRate_id     | bigint                       | YES      |     | NULL    |   X   |               |
| measuringUnit_id  | bigint                       | YES      |     | NULL    |   X   |               |
| CONSTRAINT        | unique_itemName_per_business | YES      | UNI | NULL    |   X   |               |
| itemName          | )                            | YES      |     | NULL    |       |               |

# godown_state
| Field |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id    | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| name  | varchar(100) | NO       | UNI |         |   X   |               |

# godown_godown
|     Field     |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id            | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| godownName    | varchar(100) | NO       |     |         |   X   |               |
| streetAddress | varchar(255) | YES      |     | NULL    |       |               |
| pincode       | varchar(10)  | YES      |     | NULL    |       |               |
| city          | varchar(100) | NO       |     |         |       |               |
| business_id   | bigint       | NO       |     |         |   X   |               |
| state_id      | bigint       | YES      |     | NULL    |   X   |               |

# guardian_groupobjectpermission
|      Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id              | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| object_pk       | varchar(255) | NO       |     |         |   X   |               |
| content_type_id | integer      | NO       |     |         |   X   |               |
| group_id        | integer      | NO       |     |         |   X   |               |
| permission_id   | integer      | NO       |     |         |   X   |               |

# guardian_userobjectpermission
|      Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id              | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| object_pk       | varchar(255) | NO       |     |         |   X   |               |
| content_type_id | integer      | NO       |     |         |   X   |               |
| permission_id   | integer      | NO       |     |         |   X   |               |
| user_id         | bigint       | NO       |     |         |   X   |               |

# hsn_api_hsncode
|      Field      |    Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ----------- | -------- | --- | ------- | :---: | ------------- |
| id              | integer     | NO       | PRI |         |   X   | AUTOINCREMENT |
| hsn_cd          | varchar(10) | NO       | UNI |         |   X   |               |
| hsn_description | text        | NO       |     |         |       |               |

# inventory_itemcategory
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| name        | varchar(100) | NO       |     |         |   X   |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# inventory_item
|         Field         |             Type             | Nullable | Key | Default | Index |     Extra     |
| --------------------- | ---------------------------- | -------- | --- | ------- | :---: | ------------- |
| id                    | integer                      | NO       | PRI |         |   X   | AUTOINCREMENT |
| itemName              | varchar(255)                 | NO       |     |         |       |               |
| itemType              | varchar(10)                  | NO       |     |         |       |               |
| salesPrice            | decimal                      | NO       |     |         |       |               |
| salesPriceType        | varchar(50)                  | NO       |     |         |       |               |
| purchasePrice         | decimal                      | NO       |     |         |       |               |
| purchasePriceType     | varchar(50)                  | NO       |     |         |       |               |
| itemCode              | varchar(100)                 | NO       |     |         |       |               |
| openingStock          | decimal                      | YES      |     | NULL    |       |               |
| closingStock          | decimal                      | YES      |     | NULL    |       |               |
| date                  | date                         | NO       |     |         |       |               |
| itemBatch             | varchar(50)                  | YES      |     | NULL    |       |               |
| enableLowStockWarning | bool                         | YES      |     | NULL    |       |               |
| lowStockQty           | decimal                      | YES      |     | NULL    |       |               |
| item_image            | varchar(100)                 | YES      |     | NULL    |       |               |
| description           | text                         | YES      |     | NULL    |       |               |
| hsnCode               | varchar(15)                  | YES      |     | NULL    |       |               |
| created_at            | date                         | NO       |     |         |       |               |
| business_id           | bigint                       | NO       |     |         |   X   |               |
| godown_id             | bigint                       | YES      |     | NULL    |   X   |               |
| gstTaxRate_id         | bigint                       | YES      |     | NULL    |   X   |               |
| category_id           | bigint                       | NO       |     |         |   X   |               |
| measuringUnit_id      | bigint                       | YES      |     | NULL    |   X   |               |
| CONSTRAINT            | unique_itemcode_per_business | YES      | UNI | NULL    |   X   |               |
| itemCode              | )                            | YES      |     | NULL    |       |               |

# inventory_service
|      Field       |              Type               | Nullable | Key | Default | Index |     Extra     |
| ---------------- | ------------------------------- | -------- | --- | ------- | :---: | ------------- |
| id               | integer                         | NO       | PRI |         |   X   | AUTOINCREMENT |
| serviceName      | varchar(255)                    | NO       |     |         |       |               |
| serviceType      | varchar(10)                     | NO       |     |         |       |               |
| salesPrice       | decimal                         | NO       |     |         |       |               |
| salesPriceType   | varchar(50)                     | NO       |     |         |       |               |
| sacCode          | varchar(15)                     | YES      |     | NULL    |       |               |
| serviceCode      | varchar(100)                    | NO       | UNI |         |   X   |               |
| description      | text                            | YES      |     | NULL    |       |               |
| business_id      | bigint                          | NO       |     |         |   X   |               |
| category_id      | bigint                          | NO       |     |         |   X   |               |
| gstTaxRate_id    | bigint                          | YES      |     | NULL    |   X   |               |
| measuringUnit_id | bigint                          | YES      |     | NULL    |   X   |               |
| CONSTRAINT       | unique_servicecode_per_business | YES      | UNI | NULL    |   X   |               |
| serviceCode      | )                               | YES      |     | NULL    |       |               |

# parties_partycategory
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| name        | varchar(100) | NO       |     |         |   X   |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# parties_party
|      Field       |           Type            | Nullable | Key | Default | Index |     Extra     |
| ---------------- | ------------------------- | -------- | --- | ------- | :---: | ------------- |
| id               | integer                   | NO       | PRI |         |   X   | AUTOINCREMENT |
| party_name       | varchar(250)              | NO       |     |         |       |               |
| mobile_number    | varchar(15)               | NO       |     |         |       |               |
| email            | varchar(254)              | NO       |     |         |       |               |
| gstin            | varchar(20)               | YES      |     | NULL    |       |               |
| pan              | varchar(10)               | YES      |     | NULL    |       |               |
| party_type       | varchar(10)               | NO       |     |         |       |               |
| balance_type     | varchar(10)               | NO       |     |         |       |               |
| opening_balance  | decimal                   | NO       |     |         |       |               |
| closing_balance  | decimal                   | NO       |     |         |       |               |
| shipping_address | text                      | NO       |     |         |       |               |
| billing_address  | text                      | NO       |     |         |       |               |
| street_address   | text                      | NO       |     |         |       |               |
| city             | varchar(100)              | YES      |     | NULL    |       |               |
| state            | varchar(100)              | YES      |     | NULL    |       |               |
| pincode          | varchar(10)               | YES      |     | NULL    |       |               |
| credit_period    | integer                   | NO       |     |         |       |               |
| credit_limit     | decimal                   | NO       |     |         |       |               |
| created_at       | date                      | NO       |     |         |       |               |
| business_id      | bigint                    | NO       |     |         |   X   |               |
| category_id      | bigint                    | YES      |     | NULL    |   X   |               |
| CONSTRAINT       | unique_party_per_business | YES      | UNI | NULL    |   X   |               |
| party_name       | )                         | YES      |     | NULL    |       |               |

# purchase_debitnote
|        Field         |     Type     | Nullable | Key | Default | Index |     Extra     |
| -------------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                   | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| debitnote_no         | varchar(50)  | NO       |     |         |   X   |               |
| date                 | date         | NO       |     |         |       |               |
| status               | varchar(20)  | NO       |     |         |       |               |
| is_fully_paid        | bool         | NO       |     |         |       |               |
| amount_received      | decimal      | NO       |     |         |       |               |
| balance_amount       | decimal      | NO       |     |         |       |               |
| total_amount         | decimal      | NO       |     |         |       |               |
| payment_method       | varchar(20)  | YES      |     | NULL    |       |               |
| discount             | decimal      | YES      |     | NULL    |       |               |
| taxable_amount       | decimal      | NO       |     |         |       |               |
| notes                | text         | YES      |     | NULL    |       |               |
| signature            | varchar(100) | YES      |     | NULL    |       |               |
| purchasereturn_id    | integer      | NO       |     |         |       |               |
| purchasereturn_no    | integer      | YES      |     | NULL    |       |               |
| total_payable_amount | decimal      | NO       |     |         |       |               |
| apply_tcs            | bool         | NO       |     |         |       |               |
| tcs_on               | varchar(20)  | NO       |     |         |       |               |
| tcs_amount           | decimal      | NO       |     |         |       |               |
| apply_tds            | bool         | NO       |     |         |       |               |
| tds_amount           | decimal      | NO       |     |         |       |               |
| bank_account_id      | bigint       | YES      |     | NULL    |   X   |               |
| business_id          | bigint       | NO       |     |         |   X   |               |
| party_id             | bigint       | NO       |     |         |   X   |               |
| tcs_id               | bigint       | YES      |     | NULL    |   X   |               |
| tds_id               | bigint       | YES      |     | NULL    |   X   |               |

# purchase_debitnoteitem
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity      | decimal | NO       |     |         |       |               |
| unit_price    | decimal | YES      |     | NULL    |       |               |
| amount        | decimal | YES      |     | NULL    |       |               |
| discount      | decimal | NO       |     |         |       |               |
| price_item    | decimal | YES      |     | NULL    |       |               |
| debitnote_id  | bigint  | NO       |     |         |   X   |               |
| gstTaxRate_id | bigint  | YES      |     | NULL    |   X   |               |
| item_id       | bigint  | YES      |     | NULL    |   X   |               |
| service_id    | bigint  | YES      |     | NULL    |   X   |               |

# purchase_purchase
|        Field         |     Type     | Nullable | Key | Default | Index |     Extra     |
| -------------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                   | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| purchase_no          | varchar(50)  | NO       |     |         |   X   |               |
| date                 | date         | NO       |     |         |       |               |
| status               | varchar(20)  | NO       |     |         |       |               |
| payment_term         | integer      | YES      |     | NULL    |       |               |
| due_date             | date         | YES      |     | NULL    |       |               |
| original_invoice_no  | varchar(50)  | YES      |     | NULL    |       |               |
| is_fully_paid        | bool         | NO       |     |         |       |               |
| amount_received      | decimal      | NO       |     |         |       |               |
| balance_amount       | decimal      | NO       |     |         |       |               |
| taxable_amount       | decimal      | NO       |     |         |       |               |
| total_amount         | decimal      | NO       |     |         |       |               |
| total_payable_amount | decimal      | NO       |     |         |       |               |
| apply_tcs            | bool         | NO       |     |         |       |               |
| tcs_on               | varchar(20)  | NO       |     |         |       |               |
| tcs_amount           | decimal      | NO       |     |         |       |               |
| apply_tds            | bool         | NO       |     |         |       |               |
| tds_amount           | decimal      | NO       |     |         |       |               |
| payment_method       | varchar(20)  | YES      |     | NULL    |       |               |
| discount             | decimal      | YES      |     | NULL    |       |               |
| notes                | text         | YES      |     | NULL    |       |               |
| signature            | varchar(100) | YES      |     | NULL    |       |               |
| bank_account_id      | bigint       | YES      |     | NULL    |   X   |               |
| business_id          | bigint       | YES      |     | NULL    |   X   |               |
| party_id             | bigint       | NO       |     |         |   X   |               |
| tcs_id               | bigint       | YES      |     | NULL    |   X   |               |
| tds_id               | bigint       | YES      |     | NULL    |   X   |               |

# purchase_paymentoutpurchase
|      Field      |  Type   | Nullable | Key | Default | Index |     Extra     |
| --------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id              | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| purchase_amount | decimal | NO       |     |         |       |               |
| settled_amount  | decimal | NO       |     |         |       |               |
| payment_out_id  | bigint  | NO       |     |         |   X   |               |
| purchase_id     | bigint  | NO       |     |         |   X   |               |

# purchase_paymentout
|       Field        |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------------------ | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                 | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date               | date         | NO       |     |         |       |               |
| payment_mode       | varchar(100) | NO       |     |         |       |               |
| payment_out_number | varchar(50)  | NO       |     |         |   X   |               |
| amount             | decimal      | NO       |     |         |       |               |
| notes              | text         | YES      |     | NULL    |       |               |
| bank_account_id    | bigint       | YES      |     | NULL    |   X   |               |
| business_id        | bigint       | NO       |     |         |   X   |               |
| party_id           | bigint       | NO       |     |         |   X   |               |

# purchase_purchaseitem
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity      | decimal | NO       |     |         |       |               |
| unit_price    | decimal | YES      |     | NULL    |       |               |
| amount        | decimal | YES      |     | NULL    |       |               |
| discount      | decimal | NO       |     |         |       |               |
| price_item    | decimal | YES      |     | NULL    |       |               |
| stock_updated | bool    | NO       |     |         |       |               |
| gstTaxRate_id | bigint  | YES      |     | NULL    |   X   |               |
| item_id       | bigint  | YES      |     | NULL    |   X   |               |
| purchase_id   | bigint  | NO       |     |         |   X   |               |
| service_id    | bigint  | YES      |     | NULL    |   X   |               |

# purchase_purchaseorder
|       Field       |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| purchase_order_no | varchar(50)  | NO       |     |         |   X   |               |
| date              | date         | NO       |     |         |       |               |
| status            | varchar(10)  | NO       |     |         |       |               |
| payment_term      | integer      | YES      |     | NULL    |       |               |
| balance_amount    | decimal      | NO       |     |         |       |               |
| due_date          | date         | YES      |     | NULL    |       |               |
| total_amount      | decimal      | NO       |     |         |       |               |
| discount          | decimal      | YES      |     | NULL    |       |               |
| notes             | text         | YES      |     | NULL    |       |               |
| signature         | varchar(100) | YES      |     | NULL    |       |               |
| business_id       | bigint       | NO       |     |         |   X   |               |
| party_id          | bigint       | NO       |     |         |   X   |               |

# purchase_purchaseorderitem
|      Field       |  Type   | Nullable | Key | Default | Index |     Extra     |
| ---------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id               | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity         | decimal | NO       |     |         |       |               |
| unit_price       | decimal | YES      |     | NULL    |       |               |
| amount           | decimal | YES      |     | NULL    |       |               |
| price_item       | decimal | YES      |     | NULL    |       |               |
| discount         | decimal | NO       |     |         |       |               |
| gstTaxRate_id    | bigint  | YES      |     | NULL    |   X   |               |
| item_id          | bigint  | YES      |     | NULL    |   X   |               |
| purchaseorder_id | bigint  | NO       |     |         |   X   |               |
| service_id       | bigint  | YES      |     | NULL    |   X   |               |

# purchase_purchasereturn
|        Field         |     Type     | Nullable | Key | Default | Index |     Extra     |
| -------------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                   | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| purchasereturn_no    | varchar(50)  | NO       |     |         |   X   |               |
| date                 | date         | NO       |     |         |       |               |
| status               | varchar(20)  | NO       |     |         |       |               |
| is_fully_paid        | bool         | NO       |     |         |       |               |
| amount_received      | decimal      | NO       |     |         |       |               |
| balance_amount       | decimal      | NO       |     |         |       |               |
| total_amount         | decimal      | NO       |     |         |       |               |
| taxable_amount       | decimal      | NO       |     |         |       |               |
| payment_method       | varchar(20)  | YES      |     | NULL    |       |               |
| discount             | decimal      | YES      |     | NULL    |       |               |
| notes                | text         | YES      |     | NULL    |       |               |
| signature            | varchar(100) | YES      |     | NULL    |       |               |
| purchase_id          | integer      | NO       |     |         |       |               |
| purchase_no          | integer      | YES      |     | NULL    |       |               |
| total_payable_amount | decimal      | NO       |     |         |       |               |
| apply_tcs            | bool         | NO       |     |         |       |               |
| tcs_on               | varchar(20)  | NO       |     |         |       |               |
| tcs_amount           | decimal      | NO       |     |         |       |               |
| apply_tds            | bool         | NO       |     |         |       |               |
| tds_amount           | decimal      | NO       |     |         |       |               |
| bank_account_id      | bigint       | YES      |     | NULL    |   X   |               |
| business_id          | bigint       | NO       |     |         |   X   |               |
| party_id             | bigint       | NO       |     |         |   X   |               |
| tcs_id               | bigint       | YES      |     | NULL    |   X   |               |
| tds_id               | bigint       | YES      |     | NULL    |   X   |               |

# purchase_purchasereturnitem
|       Field       |  Type   | Nullable | Key | Default | Index |     Extra     |
| ----------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id                | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity          | decimal | NO       |     |         |       |               |
| unit_price        | decimal | YES      |     | NULL    |       |               |
| amount            | decimal | YES      |     | NULL    |       |               |
| discount          | decimal | NO       |     |         |       |               |
| price_item        | decimal | YES      |     | NULL    |       |               |
| gstTaxRate_id     | bigint  | YES      |     | NULL    |   X   |               |
| item_id           | bigint  | YES      |     | NULL    |   X   |               |
| purchasereturn_id | bigint  | NO       |     |         |   X   |               |
| service_id        | bigint  | YES      |     | NULL    |   X   |               |

# reports_audittrail
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date        | datetime     | NO       |     |         |   X   |               |
| voucher_no  | varchar(50)  | NO       |     |         |       |               |
| action      | varchar(255) | NO       |     |         |       |               |
| model_name  | varchar(100) | NO       |     |         |   X   |               |
| record_id   | integer      | NO       |     |         |   X   |               |
| old_values  | text         | YES      |     | NULL    |       |               |
| new_values  | text         | YES      |     | NULL    |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |
| user_id     | bigint       | YES      |     | NULL    |   X   |               |

# reports_capitalentry
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date        | date         | NO       |     |         |       |               |
| ledger_name | varchar(255) | NO       |     |         |       |               |
| amount      | decimal      | NO       |     |         |       |               |
| created_at  | datetime     | NO       |     |         |       |               |
| updated_at  | datetime     | NO       |     |         |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# reports_currentassetentry
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date        | date         | NO       |     |         |       |               |
| ledger_name | varchar(255) | NO       |     |         |       |               |
| amount      | decimal      | NO       |     |         |       |               |
| notes       | text         | YES      |     | NULL    |       |               |
| created_at  | datetime     | NO       |     |         |       |               |
| updated_at  | datetime     | NO       |     |         |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# reports_currentliabilityentry
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date        | date         | NO       |     |         |       |               |
| ledger_name | varchar(255) | NO       |     |         |       |               |
| amount      | decimal      | NO       |     |         |       |               |
| notes       | text         | YES      |     | NULL    |       |               |
| created_at  | datetime     | NO       |     |         |       |               |
| updated_at  | datetime     | NO       |     |         |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# reports_fixedassetentry
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date        | date         | NO       |     |         |       |               |
| ledger_name | varchar(255) | NO       |     |         |       |               |
| amount      | decimal      | NO       |     |         |       |               |
| notes       | text         | YES      |     | NULL    |       |               |
| created_at  | datetime     | NO       |     |         |       |               |
| updated_at  | datetime     | NO       |     |         |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# reports_investmententry
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date        | date         | NO       |     |         |       |               |
| ledger_name | varchar(255) | NO       |     |         |       |               |
| amount      | decimal      | NO       |     |         |       |               |
| notes       | text         | YES      |     | NULL    |       |               |
| created_at  | datetime     | NO       |     |         |       |               |
| updated_at  | datetime     | NO       |     |         |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# reports_loanentry
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date        | date         | NO       |     |         |       |               |
| ledger_name | varchar(255) | NO       |     |         |       |               |
| amount      | decimal      | NO       |     |         |       |               |
| notes       | text         | YES      |     | NULL    |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# reports_loansadvanceentry
|    Field    |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id          | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date        | date         | NO       |     |         |       |               |
| ledger_name | varchar(255) | NO       |     |         |       |               |
| amount      | decimal      | NO       |     |         |       |               |
| notes       | text         | YES      |     | NULL    |       |               |
| created_at  | datetime     | NO       |     |         |       |               |
| updated_at  | datetime     | NO       |     |         |       |               |
| business_id | bigint       | NO       |     |         |   X   |               |

# sac_api_saccode
|      Field      |    Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ----------- | -------- | --- | ------- | :---: | ------------- |
| id              | integer     | NO       | PRI |         |   X   | AUTOINCREMENT |
| sac_cd          | varchar(10) | NO       | UNI |         |   X   |               |
| sac_description | text        | NO       |     |         |       |               |

# sales_creditnote
|      Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id              | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| credit_note_no  | varchar(50)  | NO       |     |         |   X   |               |
| date            | date         | NO       |     |         |       |               |
| status          | varchar(20)  | NO       |     |         |       |               |
| is_fully_paid   | bool         | NO       |     |         |       |               |
| amount_received | decimal      | NO       |     |         |       |               |
| balance_amount  | decimal      | NO       |     |         |       |               |
| total_amount    | decimal      | NO       |     |         |       |               |
| payment_method  | varchar(20)  | YES      |     | NULL    |       |               |
| discount        | decimal      | YES      |     | NULL    |       |               |
| notes           | text         | YES      |     | NULL    |       |               |
| signature       | varchar(100) | YES      |     | NULL    |       |               |
| salesreturn_id  | integer      | NO       |     |         |       |               |
| salesreturn_no  | integer      | YES      |     | NULL    |       |               |
| apply_tcs       | bool         | NO       |     |         |       |               |
| tcs_on          | varchar(20)  | NO       |     |         |       |               |
| tcs_amount      | decimal      | NO       |     |         |       |               |
| taxable_amount  | decimal      | NO       |     |         |       |               |
| bank_account_id | bigint       | YES      |     | NULL    |   X   |               |
| business_id     | bigint       | NO       |     |         |   X   |               |
| party_id        | bigint       | NO       |     |         |   X   |               |
| tcs_id          | bigint       | YES      |     | NULL    |   X   |               |

# sales_creditnoteitem
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity      | decimal | NO       |     |         |       |               |
| unit_price    | decimal | YES      |     | NULL    |       |               |
| amount        | decimal | YES      |     | NULL    |       |               |
| discount      | decimal | NO       |     |         |       |               |
| price_item    | decimal | YES      |     | NULL    |       |               |
| creditnote_id | bigint  | NO       |     |         |   X   |               |
| gstTaxRate_id | bigint  | YES      |     | NULL    |   X   |               |
| item_id       | bigint  | YES      |     | NULL    |   X   |               |
| service_id    | bigint  | YES      |     | NULL    |   X   |               |

# sales_deliverychallan
|        Field        |     Type     | Nullable | Key | Default | Index |     Extra     |
| ------------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                  | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| delivery_challan_no | varchar(50)  | NO       |     |         |   X   |               |
| date                | date         | NO       |     |         |       |               |
| status              | varchar(10)  | NO       |     |         |       |               |
| payment_term        | integer      | YES      |     | NULL    |       |               |
| balance_amount      | decimal      | NO       |     |         |       |               |
| total_amount        | decimal      | NO       |     |         |       |               |
| due_date            | date         | YES      |     | NULL    |       |               |
| discount            | decimal      | YES      |     | NULL    |       |               |
| notes               | text         | YES      |     | NULL    |       |               |
| signature           | varchar(100) | YES      |     | NULL    |       |               |
| business_id         | bigint       | NO       |     |         |   X   |               |
| party_id            | bigint       | NO       |     |         |   X   |               |

# sales_deliverychallanitem
|       Field        |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------------ | ------- | -------- | --- | ------- | :---: | ------------- |
| id                 | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity           | decimal | NO       |     |         |       |               |
| unit_price         | decimal | YES      |     | NULL    |       |               |
| amount             | decimal | YES      |     | NULL    |       |               |
| price_item         | decimal | YES      |     | NULL    |       |               |
| discount           | decimal | NO       |     |         |       |               |
| deliverychallan_id | bigint  | NO       |     |         |   X   |               |
| gstTaxRate_id      | bigint  | YES      |     | NULL    |   X   |               |
| item_id            | bigint  | YES      |     | NULL    |   X   |               |
| service_id         | bigint  | YES      |     | NULL    |   X   |               |

# sales_invoiceitem
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity      | decimal | NO       |     |         |       |               |
| unit_price    | decimal | YES      |     | NULL    |       |               |
| amount        | decimal | YES      |     | NULL    |       |               |
| discount      | decimal | NO       |     |         |       |               |
| price_item    | decimal | YES      |     | NULL    |       |               |
| gstTaxRate_id | bigint  | YES      |     | NULL    |   X   |               |
| invoice_id    | bigint  | NO       |     |         |   X   |               |
| item_id       | bigint  | YES      |     | NULL    |   X   |               |
| service_id    | bigint  | YES      |     | NULL    |   X   |               |

# sales_paymentininvoice
|     Field      |  Type   | Nullable | Key | Default | Index |     Extra     |
| -------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id             | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| invoice_amount | decimal | NO       |     |         |       |               |
| settled_amount | decimal | NO       |     |         |       |               |
| apply_tds      | bool    | NO       |     |         |       |               |
| tds_rate       | decimal | YES      |     | NULL    |       |               |
| tds_amount     | decimal | NO       |     |         |       |               |
| invoice_id     | bigint  | NO       |     |         |   X   |               |
| payment_in_id  | bigint  | NO       |     |         |   X   |               |

# sales_paymentin
|       Field       |     Type     | Nullable | Key | Default | Index |     Extra     |
| ----------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id                | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| date              | date         | NO       |     |         |       |               |
| payment_mode      | varchar(100) | NO       |     |         |       |               |
| payment_in_number | varchar(50)  | NO       |     |         |   X   |               |
| amount            | decimal      | NO       |     |         |       |               |
| notes             | text         | YES      |     | NULL    |       |               |
| bank_account_id   | bigint       | YES      |     | NULL    |   X   |               |
| business_id       | bigint       | NO       |     |         |   X   |               |
| party_id          | bigint       | NO       |     |         |   X   |               |

# sales_proforma
|     Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| -------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id             | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| proforma_no    | varchar(50)  | NO       |     |         |   X   |               |
| date           | date         | NO       |     |         |       |               |
| status         | varchar(10)  | NO       |     |         |       |               |
| payment_term   | integer      | NO       |     |         |       |               |
| due_date       | date         | YES      |     | NULL    |       |               |
| balance_amount | decimal      | NO       |     |         |       |               |
| total_amount   | decimal      | NO       |     |         |       |               |
| discount       | decimal      | YES      |     | NULL    |       |               |
| notes          | text         | YES      |     | NULL    |       |               |
| signature      | varchar(100) | YES      |     | NULL    |       |               |
| business_id    | bigint       | NO       |     |         |   X   |               |
| party_id       | bigint       | NO       |     |         |   X   |               |

# sales_proformaitem
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity      | decimal | NO       |     |         |       |               |
| unit_price    | decimal | YES      |     | NULL    |       |               |
| amount        | decimal | YES      |     | NULL    |       |               |
| price_item    | decimal | YES      |     | NULL    |       |               |
| discount      | decimal | NO       |     |         |       |               |
| gstTaxRate_id | bigint  | YES      |     | NULL    |   X   |               |
| item_id       | bigint  | YES      |     | NULL    |   X   |               |
| proforma_id   | bigint  | NO       |     |         |   X   |               |
| service_id    | bigint  | YES      |     | NULL    |   X   |               |

# sales_quotation
|     Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| -------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id             | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| quotation_no   | varchar(50)  | NO       |     |         |   X   |               |
| date           | date         | NO       |     |         |       |               |
| status         | varchar(10)  | NO       |     |         |       |               |
| payment_term   | integer      | NO       |     |         |       |               |
| balance_amount | decimal      | NO       |     |         |       |               |
| total_amount   | decimal      | NO       |     |         |       |               |
| due_date       | date         | YES      |     | NULL    |       |               |
| discount       | decimal      | YES      |     | NULL    |       |               |
| notes          | text         | YES      |     | NULL    |       |               |
| signature      | varchar(100) | YES      |     | NULL    |       |               |
| business_id    | bigint       | NO       |     |         |   X   |               |
| party_id       | bigint       | NO       |     |         |   X   |               |

# sales_quotationitem
|     Field     |  Type   | Nullable | Key | Default | Index |     Extra     |
| ------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id            | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity      | decimal | NO       |     |         |       |               |
| unit_price    | decimal | YES      |     | NULL    |       |               |
| amount        | decimal | YES      |     | NULL    |       |               |
| discount      | decimal | NO       |     |         |       |               |
| price_item    | decimal | YES      |     | NULL    |       |               |
| gstTaxRate_id | bigint  | YES      |     | NULL    |   X   |               |
| item_id       | bigint  | YES      |     | NULL    |   X   |               |
| quotation_id  | bigint  | NO       |     |         |   X   |               |
| service_id    | bigint  | YES      |     | NULL    |   X   |               |

# sales_salesreturn
|      Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id              | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| salesreturn_no  | varchar(50)  | NO       |     |         |   X   |               |
| date            | date         | NO       |     |         |       |               |
| status          | varchar(20)  | NO       |     |         |       |               |
| is_fully_paid   | bool         | NO       |     |         |       |               |
| amount_received | decimal      | NO       |     |         |       |               |
| balance_amount  | decimal      | NO       |     |         |       |               |
| total_amount    | decimal      | NO       |     |         |       |               |
| taxable_amount  | decimal      | NO       |     |         |       |               |
| payment_method  | varchar(20)  | YES      |     | NULL    |       |               |
| discount        | decimal      | YES      |     | NULL    |       |               |
| notes           | text         | YES      |     | NULL    |       |               |
| signature       | varchar(100) | YES      |     | NULL    |       |               |
| invoice_id      | integer      | NO       |     |         |       |               |
| invoice_no      | integer      | YES      |     | NULL    |       |               |
| apply_tcs       | bool         | NO       |     |         |       |               |
| tcs_on          | varchar(20)  | NO       |     |         |       |               |
| tcs_amount      | decimal      | NO       |     |         |       |               |
| bank_account_id | bigint       | YES      |     | NULL    |   X   |               |
| business_id     | bigint       | NO       |     |         |   X   |               |
| party_id        | bigint       | NO       |     |         |   X   |               |
| tcs_id          | bigint       | YES      |     | NULL    |   X   |               |

# sales_salesreturnitem
|     Field      |  Type   | Nullable | Key | Default | Index |     Extra     |
| -------------- | ------- | -------- | --- | ------- | :---: | ------------- |
| id             | integer | NO       | PRI |         |   X   | AUTOINCREMENT |
| quantity       | decimal | NO       |     |         |       |               |
| unit_price     | decimal | YES      |     | NULL    |       |               |
| amount         | decimal | YES      |     | NULL    |       |               |
| discount       | decimal | NO       |     |         |       |               |
| price_item     | decimal | YES      |     | NULL    |       |               |
| gstTaxRate_id  | bigint  | YES      |     | NULL    |   X   |               |
| item_id        | bigint  | YES      |     | NULL    |   X   |               |
| salesreturn_id | bigint  | NO       |     |         |   X   |               |
| service_id     | bigint  | YES      |     | NULL    |   X   |               |

# django_session
|    Field     |    Type     | Nullable | Key | Default | Index | Extra |
| ------------ | ----------- | -------- | --- | ------- | :---: | ----- |
| session_key  | varchar(40) | NO       | PRI |         |   X   |       |
| session_data | text        | NO       |     |         |       |       |
| expire_date  | datetime    | NO       |     |         |   X   |       |

# sales_invoice
|      Field      |     Type     | Nullable | Key | Default | Index |     Extra     |
| --------------- | ------------ | -------- | --- | ------- | :---: | ------------- |
| id              | integer      | NO       | PRI |         |   X   | AUTOINCREMENT |
| invoice_no      | varchar(50)  | NO       |     |         |   X   |               |
| date            | date         | NO       |     |         |       |               |
| status          | varchar(20)  | NO       |     |         |       |               |
| payment_term    | integer      | YES      |     | NULL    |       |               |
| due_date        | date         | YES      |     | NULL    |       |               |
| is_fully_paid   | bool         | NO       |     |         |       |               |
| amount_received | decimal      | NO       |     |         |       |               |
| balance_amount  | decimal      | NO       |     |         |       |               |
| total_amount    | decimal      | NO       |     |         |       |               |
| taxable_amount  | decimal      | NO       |     |         |       |               |
| payment_method  | varchar(20)  | YES      |     | NULL    |       |               |
| discount        | decimal      | YES      |     | NULL    |       |               |
| notes           | text         | YES      |     | NULL    |       |               |
| signature       | varchar(100) | YES      |     | NULL    |       |               |
| apply_tcs       | bool         | NO       |     |         |       |               |
| tcs_on          | varchar(20)  | NO       |     |         |       |               |
| tcs_amount      | decimal      | NO       |     |         |       |               |
| bank_account_id | bigint       | YES      |     | NULL    |   X   |               |
| business_id     | bigint       | YES      |     | NULL    |   X   |               |
| party_id        | bigint       | NO       |     |         |   X   |               |
| tcs_id          | bigint       | YES      |     | NULL    |   X   |               |
