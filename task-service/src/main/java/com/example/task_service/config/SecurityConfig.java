package com.example.task_service.config;

import com.example.task_service.security.TokenAuthenticationFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@EnableWebSecurity
@Configuration
public class SecurityConfig {

  private final TokenAuthenticationFilter tokenAuthenticationFilter;

  public SecurityConfig(
    TokenAuthenticationFilter tokenAuthenticationFilter
  ) {
    this.tokenAuthenticationFilter = tokenAuthenticationFilter;
  }

  @Bean
  public SecurityFilterChain securityFilterChain(
    HttpSecurity http
  ) throws Exception {

    http
      // API REST stateless utilisant un token JWT
      .csrf(csrf -> csrf.disable())

      // Aucune session HTTP n'est créée
      .sessionManagement(session ->
        session.sessionCreationPolicy(
          SessionCreationPolicy.STATELESS
        )
      )

      .authorizeHttpRequests(auth -> auth
        // Requêtes CORS de pré-vérification
        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()

        // Endpoints de supervision publics
        .requestMatchers(
          "/actuator/health",
          "/actuator/info"
        ).permitAll()

        // Toutes les opérations sur les tâches nécessitent un JWT valide
        .requestMatchers("/api/tasks/**").authenticated()

        // Toute autre route est refusée par défaut
        .anyRequest().denyAll()
      )

      // Vérification du JWT avant le filtre standard Spring Security
      .addFilterBefore(
        tokenAuthenticationFilter,
        UsernamePasswordAuthenticationFilter.class
      );

    return http.build();
  }
}
